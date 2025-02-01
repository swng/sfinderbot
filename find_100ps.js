const { decoder, encoder, Mino, Field } = require("tetris-fumen");
const {is_placeable, t_spin_checker, test_tspin, there_exists_tspin_slot} = require('./utils.js'); // 
const {glue} = require('./gluer.js');
const {unglue} = require('./unglueFumens.js');
const { make_sys_call } = require("./make_sys_call");
const fs = require('fs');

function combine(set_a, set_b) {
    let results = new Set();
    for (let a of set_a) {
        let pieces_a = decoder.decode(a)[0]._field.field.pieces;
        for (let b of set_b) {
            let field_b = decoder.decode(b)[0].field;
            let pieces_b = field_b.field.field.pieces;
            let no_intersection = true;
            for (let i = 0; i < 130; i++) {
                if (pieces_a[i] != 0 && pieces_a[i] != 8) {
                    if (pieces_b[i] != 0 && pieces_a[i] != 8) {
                        no_intersection = false;
                        continue;
                    } else {
                        // pieces_b is empty at i
                        pieces_b[i] = pieces_a[i];
                    }
                }
            }
            if (no_intersection) {
                results.add(encoder.encode([{ field: field_b }]));
            }
        }
    }
    return results;
}

function generate(base_field, piece) {
    let results = new Set();

    for (let col = 0; col < 10; col++) {
        for (let row = 0; row < 19; row++) {
            for (let rotation_state of ["spawn", "left", "right", "reverse"]) {
                let mino = new Mino(piece, rotation_state, col, row);
                if (mino.isValid()) {
                    let field = base_field.copy();
                    if (field.canLock(mino)) {
                        // let positions = mino.positions();
                        // field.put(mino);
                        for (let position of mino.positions()) {
                            field.set(position.x, position.y, piece);
                        }
                        // field = grey_out(field);
                        results.add(
                            encoder.encode([
                                {
                                    // bro am I wasting computation on these encodes just to decode
                                    field: field,
                                },
                            ])
                        );
                    }
                }
            }
        }
    }

    return results;
}

function merge_fumen(fumen_set) {
    let pages = [];
    for (let fumen of fumen_set) {
        pages.push(decoder.decode(fumen)[0]);
    }
    return encoder.encode(pages);
}

async function is_100(fumen, hold_piece) {
    let command = `java -jar sfinder.jar cover -K kicks/${kicks}.properties -d 180 -p '[^${hold_piece}]!' -t '${fumen}' --hold avoid`;
    let results_string = await make_sys_call(command);
    for (let line of results_string.split("\n")) {
        if (line.includes("http://fumen.zui.jp")) {
            if (line.substring(0, 3) == '100') return true;
            else return false;  
        }
    }
}

function is_placeable_last(piece, candidate) {
    let field = decoder.decode(candidate)[0].field;
    let pieces = field.field.field.pieces;

    let piece_index = ".ILOZTJS".indexOf(piece);
    for (let i = 0; i < 130; i++) {
        if (pieces[i] != 0 && pieces[i] != piece_index) pieces[i] = 8; // grey out all but the piece of interest
    }
    let temp = glue([encoder.encode([{ field: field }])])[0]; // inefficient redundant encodes and decodes but whatever
    let temp_2 = decoder.decode(temp)[0];
    let op = temp_2.operation;
    let field_2 = temp_2.field;

    return is_placeable(op, field_2);
}

function is_probably_100(fumen) {
    for (let piece of setup_pieces) {
        if (!is_placeable_last(piece, fumen)) {
            return false 
        }
    }
    return true;
}

function validCoordinates(row, col) {
    return row >= 0 && row < 20 && col >= 0 && col < 10;
}

function fillMatrix(field, row, col) {
    if (!validCoordinates(row, col)) return;

    if (field.at(col, row) != '_') return;

    field.set(col, row, 'O');

    fillMatrix(field, row + 1, col);
    fillMatrix(field, row - 1, col);
    fillMatrix(field, row, col + 1);
    fillMatrix(field, row, col - 1);
}

function noHoles(fumen) {
    let field = decoder.decode(fumen)[0].field.copy();
    loop: for(let row=18; row > 0; row--) {
        for (let col=0; col<10; col++) {
            if (field.at(col, row) == '_') {
                fillMatrix(field, row, col);
                break loop;
            }
        }
    }

    for(let row = 0; row < 17; row++) {
        for(let col = 0; col<10; col++) {
            if (field.at(col, row) == '_') {
                return false;
            }
        }
    }
    return true;
}

function noSkims(fumen) {
    let field = decoder.decode(fumen)[0].field.copy();
    for (let y = 0; y < 19; y++) {
        let line_cleared = true;
        for (let x = 0; x < 10; x++) {
            if (field.at(x, y) == '_') line_cleared = false;
        }
        if (line_cleared) return false;
    }
    return true;

}

async function main() {
    const start = performance.now();

    let initialField = decoder.decode(fumen)[0].field;
    let results = new Set([fumen]);

    for (const piece of setup_pieces) {
        const pieceResults = generate(initialField, piece);
        results = combine(pieceResults, results);
    }

    console.log(results.size + ` no ${hold_piece} 100% deepdrop nohold setups`);
    let temp = performance.now();
    console.log(`Execution Time: ${temp - start}ms`);

    if (!skims_allowed) {
        results = Array.from(results).filter(noSkims);
        console.log(results.length + ` setups after filtering out skims`);
        temp = performance.now();
        console.log(`Execution Time: ${temp - start}ms`);
    }

    if (!holes_allowed) {
        results = Array.from(results).filter(noHoles);
        console.log(results.length + ` setups after filtering out holes`);
        temp = performance.now();
        console.log(`Execution Time: ${temp - start}ms`);
    }

    results = Array.from(results).filter(is_probably_100);
    console.log(results.length + ` setups after probably100 filter`);
    temp = performance.now();
    console.log(`Execution Time: ${temp - start}ms`);

    if (do_sfinder_check) {
        // true 100% filter with sfinder. Default to false. While technically required for true 100% results, it's by far the most computationally expensive step and typically doesn't filter out much if anything.
        // Probably100 is much faster and is pretty accurate.
        let glued_candidates = glue(results);
        let true100p_results = [];
        for (candidate of glued_candidates) {
            let is_actually_100 = await is_100(candidate, hold_piece);
            if (is_actually_100) {
                true100p_results.push(unglue([candidate])[0]);
            }
        }
        console.log(true100p_results.length + ` setups after true100% filter`);
        temp = performance.now();
        console.log(`Execution Time: ${temp - start}ms`);
        results = true100p_results;
    }
    

    if (mode == "tspin") {
        let tspin_results = [];
        for (let result of results) {
            let tspin_result = there_exists_tspin_slot(result);
            if (tspin_result != undefined) {
                for (const individual_tspin_result of tspin_result) {
                    if (individual_tspin_result.lines_cleared >= min_lines_cleared && (minis_allowed || (!minis_allowed && individual_tspin_result.mini === false))) {
                        tspin_results.push(individual_tspin_result.fumen);
                    }
                }
            }
        }
        results = tspin_results;
        console.log(results.length + ` setups after tspin check finder`);
        temp = performance.now();
        console.log(`Execution Time: ${temp - start}ms`);
    } else if (mode == "immobile") {
        // will write this later
    }


    if (outputfile) {
        fs.writeFileSync(outputfile, `${merge_fumen(results)}`, 'utf8'); // Write fumen to the output file
    }


}



const GAMES = {JSTRIS: {}, TETRIO: {}, GUIDELINE: {}};
let GAME = GAMES.TETRIO;


// f"node find_100ps.js fumen={fumen} setup_pieces={setup_pieces} hold_piece={hold_piece} mode={mode} min_lines_cleared={min_lines_cleared} minis_allowed={minis_allowed} skims_allowed={skims_allowed} holes_allowed={holes_allowed} kicks={kicks} > {outputfile}"

const args = process.argv.slice(2);

let fumen = "";
let setup_pieces = "";
let hold_piece = "";
let mode = "";
let min_lines_cleared = 2;
let minis_allowed = false;
let skims_allowed = false;
let holes_allowed = false;
let kicks = "";
let outputfile = "";
let do_sfinder_check = false;

args.forEach((arg) => {
    if (arg.startsWith('fumen=')) {
        fumen = arg.slice(6);
    } else if (arg.startsWith('setup_pieces=')) {
        setup_pieces = arg.slice(13);
    } else if (arg.startsWith('hold_piece=')) {
        hold_piece = arg.slice(11);
    } else if (arg.startsWith('mode=')) {
        mode = arg.slice(5);
    } else if (arg.startsWith('min_lines_cleared=')) {
        min_lines_cleared = parseInt(arg.slice(18));
    } else if (arg.startsWith('minis_allowed=')) { 
        const value = arg.slice(14).toLowerCase();
        minis_allowed = (value === 'true' || value === 'yes');
    } else if (arg.startsWith('skims_allowed=')) {
        const value = arg.slice(14).toLowerCase();
        skims_allowed = (value === 'true' || value === 'yes');
    } else if (arg.startsWith('holes_allowed=')) {
        const value = arg.slice(14).toLowerCase();
        holes_allowed = (value === 'true' || value === 'yes');
    } else if (arg.startsWith('kicks=')) {
        kicks = arg.slice(6).toLowerCase();
        if (kicks === 'tetrio180') {
            GAME = GAMES.TETRIO;
        } else if (kicks === 'jstris180') {
            GAME = GAMES.JSTRIS;
        } else if (kicks === 'srs') {
            GAME = GAMES.GUIDELINE;
        } else {
            GAME = null; // Fallback if none match
        }
    } else if (arg.startsWith('outputfile=')) {
        outputfile = arg.slice(11);
    } else if (arg.startsWith('do_sfinder_check=')) {
        const value = arg.slice(17).toLowerCase();
        do_sfinder_check = (value === 'true' || value === 'yes');
    }
});

main();