
const { contextBridge } = require('electron')
const util = require('util');
const { spawn, exec, execFile } = require('child_process')
const execFileCommand = util.promisify(execFile);
contextBridge.exposeInMainWorld("spawn", (cmd, args, opts)=>{
    const process = spawn(cmd, args, opts)
    return {

        on: (key, callback) => process.on(key, callback),
        stdout: {on: (key, callback) => process.stdout.on(key, callback)},
        stderr: {on: (key, callback) => process.stderr.on(key, callback)},
        unref(){return process.unref()},

        ref(){return process.ref()},
        kill(){return process.kill()},
    }
})


contextBridge.exposeInMainWorld("exec", (cmd, callback)=>exec(cmd, callback))
contextBridge.exposeInMainWorld("execFile", (cmd, args)=> execFileCommand(cmd, args))