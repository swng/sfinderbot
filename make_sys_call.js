const { exec } = require("child_process");

async function make_sys_call(command) {
    return new Promise((resolve, reject) => {
        exec(command, { maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
            if (error) {
                reject(new Error(`Error: ${error.message}`));
                return;
            }
            if (stderr) {
                reject(new Error(`stderr: ${stderr}`));
                return;
            }
            resolve(stdout);
        });
    });
}

module.exports = {make_sys_call};