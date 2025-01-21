/*
Input: path.csv file generated with sfinder path command with arguments -f csv -k pattern
Output: cover.csv file
*/

const fs = require('fs');

let csv = fs.readFileSync('path.csv', 'utf8');
let rows = csv.trim().split(/\s+/).slice(1).map(s => s.split(','));
let queues_set = new Set;
let solutions_map = new Map;
for (let row of rows) {
    let queue = row[0];
    queues_set.add(queue);
    if (row[4] === '') {continue;}
    let solutions = row[4].split(';');
    for (let solution of solutions) {
        if (!solutions_map.has(solution)) {
            solutions_map.set(solution, new Set([queue]));
        } else {
            solutions_map.get(solution).add(queue);
        }
    }
}
let solutions_list = [...solutions_map.keys()];
let data = [];
for (let queue of queues_set) {
    let temp = solutions_list.map(solution => solutions_map.get(solution).has(queue) ? 'O' : 'X');
    temp.unshift(queue);
    data.push(temp);
}

content = "sequence," + solutions_list.toString();

for (row of data) {
    content += "\n" + row.toString();
}

fs.writeFile('cover.csv', content, err => {
    if (err) {
      console.error(err);
    }
    // file written successfully
  });