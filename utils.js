const { decoder, encoder, Mino, Field } = require("tetris-fumen");

const GAMES = {JSTRIS: {}, TETRIO: {}, GUIDELINE: {}};
const GAME = GAMES.TETRIO;

function there_exists_tetris_slot(fumen) {
	let field = decoder.decode(fumen)[0].field;
	for (let col = 0; col < 10; col++) {
		for (let row = 0; row < 15; row++) {
			let test_op = new Mino('I', 'right', col, row);
			if (field.canLock(test_op) && is_placeable(test_op, field)) {
				line_cleared = true;
				for (let clear_rows = row - 2; clear_rows < row + 2; clear_rows++) {
					for (let clear_cols = 0; clear_cols < 10; clear_cols++) {
						if (clear_cols != col) {
							if (field.at(clear_cols, clear_rows) == '_') line_cleared = false;
						}
					}	
				}
				if (line_cleared) {
					let temp = field.copy();
					temp.put(test_op);
					return {fumen: encoder.encode([{field: temp}])};
				}
			}
		}
	}
	return undefined;
}

function there_exists_tspin_slot(fumen) {
	let field = decoder.decode(fumen)[0].field;
	for (let row = 0; row < 15; row++) {
		for (let col = 0; col < 10; col++) {
			if (field.at(col, row) == '_') {
				let filled_adjacents = 0;
				if (occupiedCorner(field, [col+1, row])) filled_adjacents++;
				if (occupiedCorner(field, [col-1, row])) filled_adjacents++;
				if (occupiedCorner(field, [col, row+1])) filled_adjacents++;
				if (occupiedCorner(field, [col, row-1])) filled_adjacents++;

				if (filled_adjacents <= 1) {
					let filled_corners = 0;
					if (occupiedCorner(field, [col+1, row+1])) filled_corners++;
					if (occupiedCorner(field, [col-1, row+1])) filled_corners++;
					if (occupiedCorner(field, [col+1, row-1])) filled_corners++;
					if (occupiedCorner(field, [col-1, row-1])) filled_corners++;
					if (filled_corners >= 3) {
						let result = [];
						let test_op = new Mino('T', 'spawn', col, row);
						result.push(...test_tspin(test_op, field));
						test_op.rotation = 'right';
						result.push(...test_tspin(test_op, field));
						test_op.rotation = 'reverse';
						result.push(...test_tspin(test_op, field));
						test_op.rotation = 'left';
						result.push(...test_tspin(test_op, field));
						if (result.length > 0) return result;
					}
				}
				
				
			} 
		}
	}
	return undefined;
}

function test_tspin(test_op, field) {
    if (field.canLock(test_op) && is_placeable(test_op, field)) {
        let kick_index = t_spin_checker(test_op, field);
        if (kick_index != -1) {
            let temp = field.copy();
            temp.put(test_op);

            let positions = test_op.positions();

            // check for line clears
            let y_positions = new Set();
            for (let position of positions) {
                y_positions.add(position.y);
            }
            temp_rowsCleared = new Set();
            for (let y of y_positions) {
                let line_cleared = true;
                for (let x = 0; x < 10; x++) {
                    if (temp.at(x, y) == '_') line_cleared = false;
                }
                if (line_cleared) temp_rowsCleared.add(y);
            }
            // for (let row of temp_rowsCleared) rowsCleared.push(row);
            // rowsCleared.sort(function(a,b){return a-b});
            let lines_cleared = temp_rowsCleared.size;

            let mini = true;
            let four_corners = [
                [test_op.x - 1, test_op.y + 1], // northwest
                [test_op.x + 1, test_op.y + 1], // northeast
                [test_op.x + 1, test_op.y - 1], // southeast
                [test_op.x - 1, test_op.y - 1], // southwest
            ];

            let two_corners;
            switch (test_op.rotation) {
                case 'spawn':
                    two_corners = [four_corners[0], four_corners[1]];
                    break;
                case 'right':
                    two_corners = [four_corners[1], four_corners[2]];
                    break;
                case 'reverse':
                    two_corners = [four_corners[2], four_corners[3]];
                    break;
                case 'left':
                    two_corners = [four_corners[3], four_corners[0]];
                    break;
            }
            let num_corners = 0;
            for (let corner of two_corners) {
                if (occupiedCorner(field, corner)) num_corners++;
            }
            if (num_corners == 2) mini = false;

            return [ {fumen: encoder.encode([{field: temp}]), lines_cleared: lines_cleared, mini: mini }];
        }
    }
    return [];
}

function occupiedCorner(field, corner) {
	// field.at with extra check for out of bounds
	if (corner[1] < 0 || corner[0] < 0 || corner[0] > 9) return true;
	return field.at(corner[0], corner[1]) != '_';
}

function is_placeable(op, field) { // bfs I think
	// create a queue and add the initial operation
	let queue = []
	queue.push(op);

	// create a set to store visited operations
	let visited = new Set();

	// loop until the queue is empty
	while (queue.length > 0) {
		let operation = queue.pop();

		// check if the operation is placeable
		if (field.canFill(operation)) {
			// check if the piece has reached the top of the board
			let highestPoint = reverse_hd(operation, field);
			if (highestPoint.y === 20) {
				// the piece has been placed, return the cost
				return true;
			}

			// mark the operation as visited
			visited.add(op_string(operation));

			// try every possible type of movement
			let d_1_steps = [];

			let temp = spin_cw(operation, field, true);
			if (temp.length !== 0) d_1_steps = d_1_steps.concat(temp);

			temp = spin_ccw(operation, field, true);
			if (temp.length !== 0) d_1_steps = d_1_steps.concat(temp);

			temp = spin_180(operation, field, true);
			if (temp.length !== 0) d_1_steps = d_1_steps.concat(temp);
			temp = move_up(operation, 1, field);
			if (temp !== undefined) d_1_steps.push(temp);

			temp = move_right(operation, 1, field);
			if (temp !== undefined) d_1_steps.push(temp);

			temp = move_left(operation, 1, field);
			if (temp !== undefined) d_1_steps.push(temp);

			// add the next steps to the queue
			for (let step of d_1_steps) {
				let stepString = op_string(step);
				// check if the step has been visited or is already in the queue
				if (!visited.has(stepString)) {
					// calculate the heuristic and cost for this step

					// add the step to the queue
					queue.push(step);
				}
			}
		}
	}

	// if the queue is empty and no solution has been found, return false
	return false;
}

function t_spin_checker(op, field) { // returns -1 if not t spin; otherwise, returns the kick index (0-4) of the last spin used
	// console.log(page.field.str());
	// console.log("operation:", page.operation);
	// console.log(page.field.canLock(page.operation));

	if (op.type != 'T') return -1;

	let cw = vanilla_spin_cw(op.copy());
	let ccw = vanilla_spin_ccw(op.copy());

	if (field.canFill(cw)) return 0;
	//if (field.canFill(ccw)) return 0;
	//if (field.canFill(r180)) return 0;
	// if any kickless rotation is unobstructed, the other two will also be

	let cw_kicks = get_cw_kicks(cw, op.rotation);
	let ccw_kicks = get_ccw_kicks(ccw, op.rotation);

	for (let kick of cw_kicks) {
		if (field.canFill(kick)) { // try and reverse it
			let temp = vanilla_spin_ccw(kick.copy());
			let temp_kicks = get_ccw_kicks(temp, kick.rotation);
			let fail = false;
			for (let i = 0; i < 5; i++) {
				temp_kick = temp_kicks[i];
				if (field.canFill(temp_kick)) {
					// console.log(i, kick, temp_kick);
					if (temp_kick.x == op.x && temp_kick.y == op.y && !fail) return i;
                    			fail = true; // only first working kick

				}
			}
			// return -1; // only first working kick
		}
	}
	for (let kick of ccw_kicks) {
		if (field.canFill(kick)) { // try and reverse it
			let temp = vanilla_spin_cw(kick.copy());
			let temp_kicks = get_cw_kicks(temp, kick.rotation);
			let fail = false;
			for (let i = 0; i < 5; i++) {
				temp_kick = temp_kicks[i];
				if (field.canFill(temp_kick)) {
					// console.log(i, kick, temp_kick);
					if (temp_kick.x == op.x && temp_kick.y == op.y && !fail) return i;
                    			fail = true; // only first working kick
				}
			}
			// return -1; // only first working kick
		}
	}

	// XXX probably wrong on e.g. v115@zgB8HeA8IeA8AeI8BeH8CeF8JetJJ and the mirror

	if (GAME === GAMES.TETRIO) {
		// not possible to get 180 t-spins on Jstris or guideline
		let r180 = vanilla_spin_180(op.copy());
		let r180_kicks = get_180_kicks(r180, op.rotation);

		for (let kick of r180_kicks) {
			if (field.canFill(kick)) { // try and reverse it
				let temp = vanilla_spin_180(kick.copy());
				let temp_kicks = get_180_kicks(temp, kick.rotation);
				let fail = false;
				for (let i = 0; i < temp_kicks.length; i++) {
					temp_kick = temp_kicks[i];
					if (field.canFill(temp_kick)) {
						// console.log(i, kick, temp_kick);
						if (temp_kick.x == op.x && temp_kick.y == op.y && !fail) return i;
						fail = true; // only first working kick
					}
				}
				// return -1; // only first working kick
			}
		}
	}

	return -1;
}

function vanilla_spin_cw(operation) {
	let old_rotation = operation.rotation;
	switch (old_rotation) {
		case 'spawn':
			operation.rotation = 'right';
			break;
		case 'right':
			operation.rotation = 'reverse';
			break;
		case 'reverse':
			operation.rotation = 'left';
			break;
		case 'left':
			operation.rotation = 'spawn';
			break;
	}
	return operation;
}

function vanilla_spin_ccw(operation) {
	let old_rotation = operation.rotation;
	switch (old_rotation) {
		case 'spawn':
			operation.rotation = 'left';
			break;
		case 'left':
			operation.rotation = 'reverse';
			break;
		case 'reverse':
			operation.rotation = 'right';
			break;
		case 'right':
			operation.rotation = 'spawn';
			break;
	}
	return operation;
}

function vanilla_spin_180(operation) {
	let old_rotation = operation.rotation;
	switch (old_rotation) {
		case 'spawn':
			operation.rotation = 'reverse';
			break;
		case 'left':
			operation.rotation = 'right';
			break;
		case 'reverse':
			operation.rotation = 'spawn';
			break;
		case 'right':
			operation.rotation = 'left';
			break;
	}
	return operation;
}

function move_left(operation, number, field) {
	moved_operation = operation.copy();
	for (let i = 0; i < number; i++) {
		moved_operation.x--;
		if (!field.canFill(moved_operation)) return undefined;
	}
	return moved_operation;
}

function move_right(operation, number, field) {
	moved_operation = operation.copy();
	for (let i = 0; i < number; i++) {
		moved_operation.x++;
		if (!field.canFill(moved_operation)) return undefined;
	}
	return moved_operation;
}

function move_up(operation, number, field) {
	moved_operation = operation.copy();
	for (let i = 0; i < number; i++) {
		moved_operation.y++;
		if (!field.canFill(moved_operation)) return undefined;
	}
	return moved_operation;
}

function spin_cw(operation, field, reverse = false) {
	if (operation.type == 'O') return []; // let's not bother rotating O pieces
	let rotated_operation = operation.copy();
	switch (operation.rotation) {
		case 'spawn':
			rotated_operation.rotation = 'right';
			break;
		case 'right':
			rotated_operation.rotation = 'reverse';
			break;
		case 'reverse':
			rotated_operation.rotation = 'left';
			break;
		case 'left':
			rotated_operation.rotation = 'spawn';
			break;
	}

	if (reverse) {
		let kicks = get_cw_kicks(rotated_operation, operation.rotation);
		let result = [];
		for (let kick of kicks) {
			if (field.canFill(kick)) {
				let temp = spin_ccw(kick, field);
				if (temp != undefined && temp.x == operation.x && temp.y == operation.y) result.push(kick);
			}
		}
		return result;
	}

	
	let kicks = get_cw_kicks(rotated_operation, operation.rotation);
	for (let kick of kicks) {
		if (field.canFill(kick)) return kick;
	}
	return undefined;
	
}

function spin_ccw(operation, field, reverse = false) {
	if (operation.type == 'O') return []; // let's not bother rotating O pieces
	let rotated_operation = operation.copy();
	switch (operation.rotation) {
		case 'spawn':
			rotated_operation.rotation = 'left';
			break;
		case 'left':
			rotated_operation.rotation = 'reverse';
			break;
		case 'reverse':
			rotated_operation.rotation = 'right';
			break;
		case 'right':
			rotated_operation.rotation = 'spawn';
			break;
	}

	if (reverse) {
		let kicks = get_ccw_kicks(rotated_operation, operation.rotation);
		let result = [];
		for (let kick of kicks) {
			if (field.canFill(kick)) {
				let temp = spin_cw(kick, field);
				if (temp != undefined && temp.x == operation.x && temp.y == operation.y) result.push(kick);
			}
		}
		return result;
	}

	let kicks = get_ccw_kicks(rotated_operation, operation.rotation);
	for (kick of kicks) {
		if (field.canFill(kick)) return kick;
	}
	return undefined;
}

function spin_180(operation, field, reverse = false) {
	if (operation.type == 'O') return []; // let's not bother rotating O pieces
	let rotated_operation = operation.copy();
	switch (operation.rotation) {
		case 'spawn':
			rotated_operation.rotation = 'reverse';
			break;
		case 'left':
			rotated_operation.rotation = 'right';
			break;
		case 'reverse':
			rotated_operation.rotation = 'spawn';
			break;
		case 'right':
			rotated_operation.rotation = 'left';
			break;
	}

	if (reverse) {
		let kicks = get_180_kicks(rotated_operation, operation.rotation);
		let result = [];
		for (let kick of kicks) {
			if (field.canFill(kick)) {
				let temp = spin_180(kick, field);
				if (temp != undefined && temp.x == operation.x && temp.y == operation.y) result.push(kick);
			}
		}
		return result;
	}

	let kicks = get_180_kicks(rotated_operation, operation.rotation);
	for (kick of kicks) {
		if (field.canFill(kick)) return kick;
	}
	return undefined;
}

function get_cw_kicks(operation, initial_rotation) {
	let result = Array(5).fill().map(_ => operation.copy());
	if (operation.type == 'I') {
		if (GAME === GAMES.TETRIO) {
			switch (initial_rotation) {
				case 'spawn':  // 0->R
					result[0].x += 1; result[0].y += 0;
					result[1].x += 2; result[1].y += 0;
					result[2].x +=-1; result[2].y += 0;
					result[3].x +=-1; result[3].y +=-1;
					result[4].x += 2; result[4].y += 2;
					break;
				case 'right':  // R->2
					result[0].x += 0; result[0].y +=-1;
					result[1].x +=-1; result[1].y +=-1;
					result[2].x += 2; result[2].y +=-1;
					result[3].x +=-1; result[3].y += 1;
					result[4].x += 2; result[4].y +=-2;
					break;
				case 'reverse':  // 2->L
					result[0].x +=-1; result[0].y += 0;
					result[1].x += 1; result[1].y += 0;
					result[2].x +=-2; result[2].y += 0;
					result[3].x += 1; result[3].y += 1;
					result[4].x +=-2; result[4].y +=-2;
					break;
				case 'left':  // L->0
					result[0].x += 0; result[0].y += 1;
					result[1].x += 1; result[1].y += 1;
					result[2].x +=-2; result[2].y += 1;
					result[3].x += 1; result[3].y +=-1;
					result[4].x +=-2; result[4].y += 2;
					break;
			}
		} else {
			switch (initial_rotation) {
				case 'spawn':  // 0->R
					result[0].x += 1; result[0].y += 0;
					result[1].x +=-1; result[1].y += 0;
					result[2].x += 2; result[2].y += 0;
					result[3].x +=-1; result[3].y +=-1;
					result[4].x += 2; result[4].y += 2;
					break;
				case 'right':  // R->2
					result[0].x += 0; result[0].y +=-1;
					result[1].x +=-1; result[1].y +=-1;
					result[2].x += 2; result[2].y +=-1;
					result[3].x +=-1; result[3].y += 1;
					result[4].x += 2; result[4].y +=-2;
					break;
				case 'reverse':  // 2->L
					result[0].x +=-1; result[0].y += 0;
					result[1].x += 1; result[1].y += 0;
					result[2].x +=-2; result[2].y += 0;
					result[3].x += 1; result[3].y += 1;
					result[4].x +=-2; result[4].y +=-2;
					break;
				case 'left':  // L->0
					result[0].x += 0; result[0].y += 1;
					result[1].x += 1; result[1].y += 1;
					result[2].x +=-2; result[2].y += 1;
					result[3].x += 1; result[3].y +=-1;
					result[4].x +=-2; result[4].y += 2;
					break;
			}
		}
	} else {
		switch (initial_rotation) {
			case 'spawn':  // 0->R
				result[1].x -= 1;
				result[2].x -= 1; result[2].y += 1;
				                  result[3].y -= 2;
				result[4].x -= 1; result[4].y -= 2;
				break;
			case 'right':  // R->2
				result[1].x += 1;
				result[2].x += 1; result[2].y -= 1;
				                  result[3].y += 2;
				result[4].x += 1; result[4].y += 2;
				break;
			case 'reverse':  // 2->L
				result[1].x += 1;
				result[2].x += 1; result[2].y += 1;
				                  result[3].y -= 2;
				result[4].x += 1; result[4].y -= 2;
				break;
			case 'left':  // L->0
				result[1].x -= 1;
				result[2].x -= 1; result[2].y -= 1;
				                  result[3].y += 2;
				result[4].x -= 1; result[4].y += 2;
				break;
		}
	}
	return result;
}

function get_ccw_kicks(operation, initial_rotation) {
	let result = Array(5).fill().map(_ => operation.copy());
	if (operation.type == 'I') {
		if (GAME === GAMES.TETRIO) {
			switch (initial_rotation) {
				case 'spawn':  // 0->L
					result[0].x += 0; result[0].y +=-1;
					result[1].x +=-1; result[1].y +=-1;
					result[2].x += 2; result[2].y +=-1;
					result[3].x += 2; result[3].y +=-2;
					result[4].x +=-1; result[4].y += 1;
					break;
				case 'left':  // L->2
					result[0].x += 1; result[0].y += 0;
					result[1].x += 2; result[1].y += 0;
					result[2].x +=-1; result[2].y += 0;
					result[3].x += 2; result[3].y += 2;
					result[4].x +=-1; result[4].y +=-1;
					break;
				case 'reverse':  // 2->R
					result[0].x += 0; result[0].y += 1;
					result[1].x +=-2; result[1].y += 1;
					result[2].x += 1; result[2].y += 1;
					result[3].x +=-2; result[3].y += 2;
					result[4].x += 1; result[4].y +=-1;
					break;
				case 'right':  // R->0
					result[0].x +=-1; result[0].y += 0;
					result[1].x +=-2; result[1].y += 0;
					result[2].x += 1; result[2].y += 0;
					result[3].x +=-2; result[3].y +=-2;
					result[4].x += 1; result[4].y += 1;
					break;
			}
		} else {
			switch (initial_rotation) {
				case 'spawn':  // 0->L
					result[0].x += 0; result[0].y +=-1;
					result[1].x +=-1; result[1].y +=-1;
					result[2].x += 2; result[2].y +=-1;
					result[3].x +=-1; result[3].y += 1;
					result[4].x += 2; result[4].y +=-2;
					break;
				case 'left':  // L->2
					result[0].x += 1; result[0].y += 0;
					result[1].x +=-1; result[1].y += 0;
					result[2].x += 2; result[2].y += 0;
					result[3].x +=-1; result[3].y +=-1;
					result[4].x += 2; result[4].y += 2;
					break;
				case 'reverse':  // 2->R
					result[0].x += 0; result[0].y += 1;
					result[1].x += 1; result[1].y += 1;
					result[2].x +=-2; result[2].y += 1;
					result[3].x += 1; result[3].y +=-1;
					result[4].x +=-2; result[4].y += 2;
					break;
				case 'right':  // R->0
					result[0].x +=-1; result[0].y += 0;
					result[1].x += 1; result[1].y += 0;
					result[2].x +=-2; result[2].y += 0;
					result[3].x += 1; result[3].y += 1;
					result[4].x +=-2; result[4].y +=-2;
					break;
			}
		}
	} else {
		switch (initial_rotation) {
			case 'spawn':  // 0->L
				result[1].x += 1;
				result[2].x += 1; result[2].y += 1;
				                  result[3].y -= 2;
				result[4].x += 1; result[4].y -= 2;
				break;
			case 'left':  // L->2
				result[1].x -= 1;
				result[2].x -= 1; result[2].y -= 1;
				                  result[3].y += 2;
				result[4].x -= 1; result[4].y += 2;
				break;
			case 'reverse':  // 2->R
				result[1].x -= 1;
				result[2].x -= 1; result[2].y += 1;
				                  result[3].y -= 2;
				result[4].x -= 1; result[4].y -= 2;
				break;
			case 'right':  // R->0
				result[1].x += 1;
				result[2].x += 1; result[2].y -= 1;
				                  result[3].y += 2;
				result[4].x += 1; result[4].y += 2;
				break;
		}
	}
	return result;
}

function get_180_kicks(operation, initial_rotation) {
	if (GAME === GAMES.GUIDELINE) {throw 'guideline has no 180';}
	if (operation.type == 'I') {
		// Jstris and tetr.io have the same 180 I kicks
		let result = Array(2).fill().map(_ => operation.copy());
		switch (initial_rotation) {
			case 'spawn':  // 0->2
				result[0].x += 1; result[0].y -= 1;
				result[1].x += 1; result[1].y += 0;
				break;
			case 'left':  // L->R
				result[0].x += 1; result[0].y += 1;
				result[1].x += 0; result[1].y += 1;
				break;
			case 'reverse':	 // 2->0
				result[0].x -= 1; result[0].y += 1;
				result[1].x -= 1; result[1].y += 0;
				break;
			case 'right':  // R->L
				result[0].x -= 1; result[0].y -= 1;
				result[1].x += 0; result[1].y -= 1;
				break;
		}
		// only 180 kick is the immobile one for I pieces I guess
		return result.slice(0, 2);
	}
	let result;
	switch (GAME) {
		case GAMES.TETRIO:
			result = Array(6).fill().map(_ => operation.copy());
			switch (initial_rotation) { // using SRS+ kickset here
				case 'spawn':  // 0->2
					                  result[1].y += 1;
					result[2].x += 1; result[2].y += 1;
					result[3].x -= 1; result[3].y += 1;
					result[4].x += 1;
					result[5].x -= 1;
					break;
				case 'left':  // L->R
					result[1].x -= 1;
					result[2].x -= 1; result[2].y += 2;
					result[3].x -= 1; result[3].y += 1;
					                  result[4].y += 2;
					                  result[5].y += 1;
					break;
				case 'reverse':  // 2->0
					                  result[1].y -= 1;
					result[2].x -= 1; result[2].y -= 1;
					result[3].x += 1; result[3].y -= 1;
					result[4].x -= 1;
					result[5].x += 1;
					break;
				case 'right':  // R->L
					result[1].x += 1;
					result[2].x += 1; result[2].y += 2;
					result[3].x += 1; result[3].y += 1;
					                  result[4].y += 2;
					                  result[5].y += 1;
					break;
			}
			return result;
		case GAMES.JSTRIS:
			result = Array(2).fill().map(_ => operation.copy());
			switch (initial_rotation) {
				case 'spawn':  // 0->2
					result[1].y += 1;
					break;
				case 'left':  // L->R
					result[1].x -= 1;
					break;
				case 'reverse':  // 2->0
					result[1].y -= 1;
					break;
				case 'right':  // R->L
					result[1].x += 1;
					break;
			}
			return result;
	}
	return result;
}

function reverse_hd(base_operation, field) {
	let operation = base_operation.copy();
	while (field.canFill(operation) && operation.y < 21) {
		operation.y++;
	}
	operation.y--;

	return operation;
}

function op_string(operation) {
	return operation.rotation + operation.x + operation.y;
}

module.exports = {is_placeable, t_spin_checker, test_tspin, there_exists_tspin_slot, there_exists_tetris_slot};