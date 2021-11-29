
const { contextBridge } = require('electron')
const {promisify} = require('util');
const { spawn, exec } = require('child_process');
const execCommand = promisify(exec);

contextBridge.exposeInMainWorld("spawn", (cmd, args=[], opts={})=>{

    const process = spawn(cmd, args, opts)
    
    return {
        on: (key, callback) => process.on(key, callback),

        stdout: {on: (key, callback) => process.stdout.on(key, callback)},
        stderr: {on: (key, callback) => process.stderr.on(key, callback)},
        unref(){return process.unref()},
        ref(){return process.ref()},
        kill(){return process.kill()}
    }
})

contextBridge.exposeInMainWorld("exec", async (cmd)=>{
    console.log(`Executing command: ${cmd}`)
    let data, error;
    try {
        data = await execCommand(cmd)
        console.log(`Execution completed: \n${cmd}\n --> `, data)
    } catch (err) {
        console.error(err)
        error = err
        console.log(`Erro occured while executing command: ${cmd}`)
    }
    return [data, error]
})

contextBridge.exposeInMainWorld("promisify", (fn) => promisify(fn))

