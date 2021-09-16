
const { contextBridge } = require('electron')
const { spawn, exec } = require('child_process')

contextBridge.exposeInMainWorld("spawn", (cmd, args, opts)=>{
    const process = spawn(cmd, args, opts)
    return {

        on: (key, callback) => process.on(key, callback),
        stdout: {on: (key, callback) => process.on(key, callback)},
        stderr: {on: (key, callback) => process.on(key, callback)},
        unref(){return process.unref()},

        ref(){return process.ref()}
    }
})
contextBridge.exposeInMainWorld("exec", (cmd, callback)=>exec(cmd, callback))