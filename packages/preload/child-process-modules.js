
import { contextBridge } from 'electron'
import { promisify } from 'util'
import { spawn, exec, execSync } from 'child_process'
const execCommand = promisify(exec);

contextBridge.exposeInMainWorld("spawn", (cmd, args=[], opts={})=>{

    const process = spawn(cmd, args, opts)
    console.log(`Spawned child pid: ${process.pid}`)

    return {
    
        pid: process.pid,
        killed: process.killed,
        ref(){return process.ref()},
        unref(){return process.unref()},
        kill(signal=2){return process.kill(signal)},
        on: (key, callback) => process.on(key, callback),
        stdout: {on: (key, callback) => process.stdout.on(key, callback)},
        stderr: {on: (key, callback) => process.stderr.on(key, callback)},
        
    }
})


export const computeExecCommand = async (cmd) => {
    console.log(`Executing command: ${cmd}`)
    let error;
    let stdout, stderr;
    try {

        ({stdout, stderr} = await execCommand(cmd));
    } catch (err) {
        console.error(err)
        error = err
        console.log(`Erro occured while executing command: ${cmd}`)
    }
    const data = {stdout, stderr}
    console.log(`Execution completed: \n${cmd}\n --> `, data)

    return [data, error]
}

contextBridge.exposeInMainWorld("exec", computeExecCommand)
contextBridge.exposeInMainWorld("promisify", (fn) => promisify(fn))
contextBridge.exposeInMainWorld("execSync", execSync)
