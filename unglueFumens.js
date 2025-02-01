const { decoder, encoder} = require('tetris-fumen');

pieces = {
    T: [
        [[0, 0], [0, -1], [0, 1], [1, 0]],
        [[0, 0], [0, 1], [1, 0], [-1, 0]],
        [[0, 0], [0, -1], [0, 1], [-1, 0]],
        [[0, 0], [0, -1], [1, 0], [-1, 0]]
    ],
    I: [
        [[0, 0], [0, -1], [0, 1], [0, 2]],
        [[0, 0], [1, 0], [-1, 0], [-2, 0]],
        [[0, 0], [0, -1], [0, -2], [0, 1]],
        [[0, 0], [1, 0], [2, 0], [-1, 0]]
    ],
    L: [
        [[0, 0], [0, -1], [0, 1], [1, 1]],
        [[0, 0], [1, 0], [-1, 0], [-1, 1]],
        [[0, 0], [0, -1], [0, 1], [-1, -1]],
        [[0, 0], [1, -1], [1, 0], [-1, 0]]
    ],
    J: [
        [[0, 0], [0, -1], [0, 1], [1, -1]],
        [[0, 0], [1, 0], [-1, 0], [1, 1]],
        [[0, 0], [0, -1], [0, 1], [-1, 1]],
        [[0, 0], [-1, -1], [1, 0], [-1, 0]]
    ],
    S: [
        [[0, 0], [0, -1], [1, 0], [1, 1]],
        [[0, 0], [1, 0], [0, 1], [-1, 1]],
        [[0, 0], [0, 1], [-1, 0], [-1, -1]],
        [[0, 0], [-1, 0], [0, -1], [1, -1]]
    ],
    Z: [
        [[0, 0], [0, 1], [1, 0], [1, -1]],
        [[0, 0], [-1, 0], [0, 1], [1, 1]],
        [[0, 0], [0, -1], [-1, 0], [-1, 1]],
        [[0, 0], [1, 0], [0, -1], [-1, -1]]
    ],
    O: [
        [[0, 0], [1, 0], [0, 1], [1, 1]],
        [[0, 0], [0, 1], [-1, 0], [-1, 1]],
        [[0, 0], [-1, 0], [0, -1], [-1, -1]],
        [[0, 0], [0, -1], [1, -1], [1, 0]]
    ]
}

rotationMapping = {
    "spawn": 0,
    "right": 1,
    "reverse": 2,
    "left": 3
}

colorMapping = {
    "S": 7,
    "J": 6,
    "T": 5,
    "Z": 4,
    "O": 3,
    "L": 2,
    "I": 1
}

function clearedOffset(rowsCleared, yIndex) {
    for (let row of rowsCleared) {
        if (yIndex >= row) yIndex++;
    }
    return yIndex;
}


function unglue(fumenCodes) {
    let results = []
    for (let code of fumenCodes) {
        let inputPages = decoder.decode(code);
        board = inputPages[0]["_field"]["field"]["pieces"];
        rowsCleared = [];

        for (let pageNum = 0; pageNum < inputPages.length; pageNum++) {
            op = inputPages[pageNum]["operation"];
            piece = pieces[op["type"]][rotationMapping[op["rotation"]]];

            for (let mino of piece) {
                yIndex = op.y + mino[0];
                yIndex = clearedOffset(rowsCleared, yIndex);
                xIndex = op.x + mino[1];
                index = yIndex * 10 + xIndex;
                if (board[index] != 0) {
                    console.log("error");
                } // some intersect with the board
                board[index] = colorMapping[op["type"]];
            }

            temp = [];

            for (let y = -2; y < 3; y++) { // rows in which the piece might have been
                yIndex = op.y + y;
                yIndex = clearedOffset(rowsCleared, yIndex);
                if (yIndex >= 0) { // sanity check
                    rowCleared = true;
                    for (let x = 0; x < 10; x++) {
                        index = yIndex * 10 + x;
                        rowCleared = rowCleared && (board[index] != 0);
                    }
                    if (rowCleared) {
                        temp.push(yIndex);
                    }
                }
            }

            for (let row of temp) {
                if (!rowsCleared.includes(row)) {
                    rowsCleared.push(row);
                    rowsCleared.sort(function (a, b) {
                        return a - b
                    });
                }
            }

        }

        let outputPages = [inputPages[0]]; // lazily generating output fumen by destructively modifying the input
        outputPages[0]["operation"] = undefined;
        outputPages[0]["_field"]["field"]["pieces"] = board;

        results.push(encoder.encode(outputPages));

    }

    return results
}


module.exports = {unglue};
