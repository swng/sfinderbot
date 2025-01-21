const { encoder, decoder, Page, Field } = require("tetris-fumen");

const GAMES = { JSTRIS: {}, TETRIO: {}, GUIDELINE: {} };
const DROPS = { SLOW: {}, INSTANT: {}, GRAVITY: {} }; // for sd, gravity is 20G

let directions = decoder.decode(process.argv[2]);

let placement = directions[0];

let GAME;
switch (process.argv[3]) {
  case "jstris":
    GAME = GAMES.JSTRIS;
    break;
  case "tetrio":
    GAME = GAMES.TETRIO;
    break;
  case "guidline":
    GAME = GAMES.GUIDELINE;
    break;
}

let DROP;
switch (process.argv[4]) {
  case "slow":
    DROP = DROPS.SLOW;
    break;
  case "instant":
    DROP = DROPS.INSTANT;
    break;
  case "20g":
    DROP = DROPS.GRAVITY;
    break;
}



function move_left(operation, field) {
	if (!field.canFill(operation)) return undefined;
	moved_operation = operation.copy();
	moved_operation.x--;
	if (!field.canFill(moved_operation)) return undefined;
	return moved_operation;
}

function DAS_left(operation, field) {
	if (!field.canFill(operation)) return undefined;
	let moved_operation = operation.copy();
	while (field.canFill(moved_operation)) {
		moved_operation.x--;
	}
	moved_operation.x++;
	return moved_operation;
}

function move_right(operation, field) {
	if (!field.canFill(operation)) return undefined;
	moved_operation = operation.copy();
	moved_operation.x++;
	if (!field.canFill(moved_operation)) return undefined;
	return moved_operation;
}

function DAS_right(operation, field) {
	if (!field.canFill(operation)) return undefined;
	let moved_operation = operation.copy();
	while (field.canFill(moved_operation)) {
		moved_operation.x++;
	}
	moved_operation.x--;
	return moved_operation;
}

function move_down(operation, field) {
	if (!field.canFill(operation)) return undefined;
	moved_operation = operation.copy();
	moved_operation.y--;
	if (!field.canFill(moved_operation)) return undefined;
	return moved_operation;
}

function DAS_down(operation, field) {
	let moved_operation = operation.copy();
	while (!field.canLock(moved_operation)) {
		moved_operation.y--;
	}
	return moved_operation;

}

function spin_cw(operation, field) {
	if (operation.type == 'O') return operation; // let's not bother rotating O pieces
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
	
	let kicks = get_cw_kicks(rotated_operation, operation.rotation);
	for (let kick of kicks) {
		if (field.canFill(kick)) return kick;
	}
	return undefined;
	
}

function spin_ccw(operation, field) {
	if (operation.type == 'O') return operation; // let's not bother rotating O pieces
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

	let kicks = get_ccw_kicks(rotated_operation, operation.rotation);
	for (let kick of kicks) {
		if (field.canFill(kick)) return kick;
	}
	return undefined;
}

function spin_180(operation, field) {
	if (operation.type == 'O') return operation; // let's not bother rotating O pieces
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

	let kicks = get_180_kicks(rotated_operation, operation.rotation);
	for (let kick of kicks) {
		if (field.canFill(kick)) return kick;
	}
	return undefined;
}

function get_cw_kicks(operation, initial_rotation) {
    let result = Array(5)
        .fill()
        .map((_) => operation.copy());
    if (operation.type == "I") {
        if (GAME === GAMES.TETRIO) {
            switch (initial_rotation) {
                case "spawn": // 0->R
                    result[0].x += 1;
                    result[0].y += 0;
                    result[1].x += 2;
                    result[1].y += 0;
                    result[2].x += -1;
                    result[2].y += 0;
                    result[3].x += -1;
                    result[3].y += -1;
                    result[4].x += 2;
                    result[4].y += 2;
                    break;
                case "right": // R->2
                    result[0].x += 0;
                    result[0].y += -1;
                    result[1].x += -1;
                    result[1].y += -1;
                    result[2].x += 2;
                    result[2].y += -1;
                    result[3].x += -1;
                    result[3].y += 1;
                    result[4].x += 2;
                    result[4].y += -2;
                    break;
                case "reverse": // 2->L
                    result[0].x += -1;
                    result[0].y += 0;
                    result[1].x += 1;
                    result[1].y += 0;
                    result[2].x += -2;
                    result[2].y += 0;
                    result[3].x += 1;
                    result[3].y += 1;
                    result[4].x += -2;
                    result[4].y += -2;
                    break;
                case "left": // L->0
                    result[0].x += 0;
                    result[0].y += 1;
                    result[1].x += 1;
                    result[1].y += 1;
                    result[2].x += -2;
                    result[2].y += 1;
                    result[3].x += 1;
                    result[3].y += -1;
                    result[4].x += -2;
                    result[4].y += 2;
                    break;
            }
        } else {
            switch (initial_rotation) {
                case "spawn": // 0->R
                    result[0].x += 1;
                    result[0].y += 0;
                    result[1].x += -1;
                    result[1].y += 0;
                    result[2].x += 2;
                    result[2].y += 0;
                    result[3].x += -1;
                    result[3].y += -1;
                    result[4].x += 2;
                    result[4].y += 2;
                    break;
                case "right": // R->2
                    result[0].x += 0;
                    result[0].y += -1;
                    result[1].x += -1;
                    result[1].y += -1;
                    result[2].x += 2;
                    result[2].y += -1;
                    result[3].x += -1;
                    result[3].y += 1;
                    result[4].x += 2;
                    result[4].y += -2;
                    break;
                case "reverse": // 2->L
                    result[0].x += -1;
                    result[0].y += 0;
                    result[1].x += 1;
                    result[1].y += 0;
                    result[2].x += -2;
                    result[2].y += 0;
                    result[3].x += 1;
                    result[3].y += 1;
                    result[4].x += -2;
                    result[4].y += -2;
                    break;
                case "left": // L->0
                    result[0].x += 0;
                    result[0].y += 1;
                    result[1].x += 1;
                    result[1].y += 1;
                    result[2].x += -2;
                    result[2].y += 1;
                    result[3].x += 1;
                    result[3].y += -1;
                    result[4].x += -2;
                    result[4].y += 2;
                    break;
            }
        }
    } else {
        switch (initial_rotation) {
            case "spawn": // 0->R
                result[1].x -= 1;
                result[2].x -= 1;
                result[2].y += 1;
                result[3].y -= 2;
                result[4].x -= 1;
                result[4].y -= 2;
                break;
            case "right": // R->2
                result[1].x += 1;
                result[2].x += 1;
                result[2].y -= 1;
                result[3].y += 2;
                result[4].x += 1;
                result[4].y += 2;
                break;
            case "reverse": // 2->L
                result[1].x += 1;
                result[2].x += 1;
                result[2].y += 1;
                result[3].y -= 2;
                result[4].x += 1;
                result[4].y -= 2;
                break;
            case "left": // L->0
                result[1].x -= 1;
                result[2].x -= 1;
                result[2].y -= 1;
                result[3].y += 2;
                result[4].x -= 1;
                result[4].y += 2;
                break;
        }
    }
    return result;
}

function get_ccw_kicks(operation, initial_rotation) {
    let result = Array(5)
        .fill()
        .map((_) => operation.copy());
    if (operation.type == "I") {
        if (GAME === GAMES.TETRIO) {
            switch (initial_rotation) {
                case "spawn": // 0->L
                    result[0].x += 0;
                    result[0].y += -1;
                    result[1].x += -1;
                    result[1].y += -1;
                    result[2].x += 2;
                    result[2].y += -1;
                    result[3].x += 2;
                    result[3].y += -2;
                    result[4].x += -1;
                    result[4].y += 1;
                    break;
                case "left": // L->2
                    result[0].x += 1;
                    result[0].y += 0;
                    result[1].x += 2;
                    result[1].y += 0;
                    result[2].x += -1;
                    result[2].y += 0;
                    result[3].x += 2;
                    result[3].y += 2;
                    result[4].x += -1;
                    result[4].y += -1;
                    break;
                case "reverse": // 2->R
                    result[0].x += 0;
                    result[0].y += 1;
                    result[1].x += -2;
                    result[1].y += 1;
                    result[2].x += 1;
                    result[2].y += 1;
                    result[3].x += -2;
                    result[3].y += 2;
                    result[4].x += 1;
                    result[4].y += -1;
                    break;
                case "right": // R->0
                    result[0].x += -1;
                    result[0].y += 0;
                    result[1].x += -2;
                    result[1].y += 0;
                    result[2].x += 1;
                    result[2].y += 0;
                    result[3].x += -2;
                    result[3].y += -2;
                    result[4].x += 1;
                    result[4].y += 1;
                    break;
            }
        } else {
            switch (initial_rotation) {
                case "spawn": // 0->L
                    result[0].x += 0;
                    result[0].y += -1;
                    result[1].x += -1;
                    result[1].y += -1;
                    result[2].x += 2;
                    result[2].y += -1;
                    result[3].x += -1;
                    result[3].y += 1;
                    result[4].x += 2;
                    result[4].y += -2;
                    break;
                case "left": // L->2
                    result[0].x += 1;
                    result[0].y += 0;
                    result[1].x += -1;
                    result[1].y += 0;
                    result[2].x += 2;
                    result[2].y += 0;
                    result[3].x += -1;
                    result[3].y += -1;
                    result[4].x += 2;
                    result[4].y += 2;
                    break;
                case "reverse": // 2->R
                    result[0].x += 0;
                    result[0].y += 1;
                    result[1].x += 1;
                    result[1].y += 1;
                    result[2].x += -2;
                    result[2].y += 1;
                    result[3].x += 1;
                    result[3].y += -1;
                    result[4].x += -2;
                    result[4].y += 2;
                    break;
                case "right": // R->0
                    result[0].x += -1;
                    result[0].y += 0;
                    result[1].x += 1;
                    result[1].y += 0;
                    result[2].x += -2;
                    result[2].y += 0;
                    result[3].x += 1;
                    result[3].y += 1;
                    result[4].x += -2;
                    result[4].y += -2;
                    break;
            }
        }
    } else {
        switch (initial_rotation) {
            case "spawn": // 0->L
                result[1].x += 1;
                result[2].x += 1;
                result[2].y += 1;
                result[3].y -= 2;
                result[4].x += 1;
                result[4].y -= 2;
                break;
            case "left": // L->2
                result[1].x -= 1;
                result[2].x -= 1;
                result[2].y -= 1;
                result[3].y += 2;
                result[4].x -= 1;
                result[4].y += 2;
                break;
            case "reverse": // 2->R
                result[1].x -= 1;
                result[2].x -= 1;
                result[2].y += 1;
                result[3].y -= 2;
                result[4].x -= 1;
                result[4].y -= 2;
                break;
            case "right": // R->0
                result[1].x += 1;
                result[2].x += 1;
                result[2].y -= 1;
                result[3].y += 2;
                result[4].x += 1;
                result[4].y += 2;
                break;
        }
    }
    return result;
}

function get_180_kicks(operation, initial_rotation) {
    if (GAME === GAMES.GUIDELINE) {
        throw "guideline has no 180";
    }
    if (operation.type == "I") {
        // Jstris and tetr.io have the same 180 I kicks
        let result = Array(2)
            .fill()
            .map((_) => operation.copy());
        switch (initial_rotation) {
            case "spawn": // 0->2
                result[0].x += 1;
                result[0].y -= 1;
                result[1].x += 1;
                result[1].y += 0;
                break;
            case "left": // L->R
                result[0].x += 1;
                result[0].y += 1;
                result[1].x += 0;
                result[1].y += 1;
                break;
            case "reverse": // 2->0
                result[0].x -= 1;
                result[0].y += 1;
                result[1].x -= 1;
                result[1].y += 0;
                break;
            case "right": // R->L
                result[0].x -= 1;
                result[0].y -= 1;
                result[1].x += 0;
                result[1].y -= 1;
                break;
        }
        // only 180 kick is the immobile one for I pieces I guess
        return result.slice(0, 2);
    }
    let result;
    switch (GAME) {
        case GAMES.TETRIO:
            result = Array(6)
                .fill()
                .map((_) => operation.copy());
            switch (
                initial_rotation // using SRS+ kickset here
                ) {
                case "spawn": // 0->2
                    result[1].y += 1;
                    result[2].x += 1;
                    result[2].y += 1;
                    result[3].x -= 1;
                    result[3].y += 1;
                    result[4].x += 1;
                    result[5].x -= 1;
                    break;
                case "left": // L->R
                    result[1].x -= 1;
                    result[2].x -= 1;
                    result[2].y += 2;
                    result[3].x -= 1;
                    result[3].y += 1;
                    result[4].y += 2;
                    result[5].y += 1;
                    break;
                case "reverse": // 2->0
                    result[1].y -= 1;
                    result[2].x -= 1;
                    result[2].y -= 1;
                    result[3].x += 1;
                    result[3].y -= 1;
                    result[4].x -= 1;
                    result[5].x += 1;
                    break;
                case "right": // R->L
                    result[1].x += 1;
                    result[2].x += 1;
                    result[2].y += 2;
                    result[3].x += 1;
                    result[3].y += 1;
                    result[4].y += 2;
                    result[5].y += 1;
                    break;
            }
            return result;
        case GAMES.JSTRIS:
            result = Array(2)
                .fill()
                .map((_) => operation.copy());
            switch (initial_rotation) {
                case "spawn": // 0->2
                    result[1].y += 1;
                    break;
                case "left": // L->R
                    result[1].x -= 1;
                    break;
                case "reverse": // 2->0
                    result[1].y -= 1;
                    break;
                case "right": // R->L
                    result[1].x += 1;
                    break;
            }
            return result;
    }
    return result;
}

function op_string(operation) {
    return operation.rotation + operation.x + operation.y;
}

function construct_path(path, initial, final) {
	let moves = [];
  let operations = [];
	let current = final.copy();

	moves.unshift(current);
  operations.unshift(current);
	let prev = path[op_string(current)];

	while (prev != undefined) {
		moves.unshift(prev.move);
    operations.unshift(prev.operation);
    
		current = prev.operation;
		prev = path[op_string(current)];

	}
	moves.pop();

  const pages = [];

  for (const operation of operations) {
    pages.push({
      field: placement.field,
      operation: operation,
    });
  }
  
  return [moves, encoder.encode(pages)];
}

let inputs = ["softDrop", "rotateCW", "rotateCCW", "moveRight", "moveLeft", "DAS_right", "DAS_left"]; // in the fixed arbitrary order we add them here

if (GAME != GAMES.GUIDELINE) {
  inputs.splice(3, 0, "rotate180")
}

if (DROP == DROPS.SLOW) {
  inputs.push("move_down")
}


function placement_path_center(final, field) { // bfs I think
	// create spawn operation
	let initial = final.copy();
	initial.rotation = 'spawn';
	initial.x = 4;

  if (GAME == GAMES.TETRIO) {
    initial.y = 20;
  }
	else {
    initial.y = 19;
  }
  
	// create a queue and add the initial operation
	let queue = [];
	queue.push({operation: initial.copy(), prev: undefined});

    let path = {};

	// create a set to store visited operations
	let visited = new Set();
	visited.add(op_string(initial))

	// loop until the queue is empty
	while (queue.length > 0) {
		let next = queue.pop();
        let operation = next.operation;

		// check if the operation is placeable
		if (field.canFill(operation)) {
			// check if the piece has reached the destination
			if ((operation.x == final.x) && (operation.y == final.y) && (operation.rotation == final.rotation)) {
				return construct_path(path, initial, final);
			}

			// try every possible type of movement
			let d_1_steps = [];

			d_1_steps.push(DAS_down(operation, field));


			if (DROP != DROPS.GRAVITY || field.canLock(operation)) { // if 20g, dont allow inputs in midair
        if (GAME != GAMES.GUIDLINE) {
           d_1_steps.push(spin_180(operation, field)); 
        }

				d_1_steps.push(move_right(operation, field));
				d_1_steps.push(move_left(operation, field));
        
        if (DROP != DROPS.GRAVITY || field.canLock(move_right(operation, field))) {
          d_1_steps.push(DAS_right(operation, field));
        }
				if (DROP != DROPS.GRAVITY || field.canLock(move_left(operation, field))) {
          d_1_steps.push(DAS_left(operation, field));
        }

        if (DROP == DROPS.SLOW) {
          d_1_steps.push(move_down(operation, field));
        }
			}

			// add the next steps to the queue
			d_1_steps.forEach((step, i) => {
				if (step !== undefined) {
					let stepString = op_string(step);
					// check if the step has been visited or is already in the queue
					if (!visited.has(stepString)) {
						// add the step to the queue
						queue.unshift({operation: step, prev: operation});
						visited.add(stepString);
						path[stepString] = {operation: operation, move: inputs[i]};
						// path.push({operation: step, prev: operation});
					}
				}
			})
		}
	}

	// if the queue is empty and no solution has been found, return undefined
	return ["fuck you"];
}

let a = placement_path_center(placement.operation, placement.field);

console.log(a.join("\n"));