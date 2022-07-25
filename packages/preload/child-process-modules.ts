import { exposeInMainWorld } from './exposeInMainWorld'
import { promisify } from 'util'
import * as child from 'child_process';
// import { spawn, exec, execSync } from 'child_process'
const execSync = child.execSync
export { execSync }
const execCommand = promisify(child.exec)

export const spawnFn = (cmd: string, args: readonly string[] = [], opts?: child.SpawnOptionsWithoutStdio | undefined) => {
    const process = child.spawn(cmd, args, opts)
    console.log(`Spawned child pid: ${process.pid}`)
    return {
        pid: process.pid,
        killed: process.killed,
        ref() {
            return process.ref()
        },
        unref() {
            return process.unref()
        },
        kill(signal = 2) {
            return process.kill(signal)
        },
        on: (key: string, callback: (...args: any[]) => void) => process.on(key, callback),
        stdout: { on: (key: string, callback: (...args: any[]) => void) => process.stdout.on(key, callback) },
        stderr: { on: (key: string, callback: (...args: any[]) => void) => process.stderr.on(key, callback) },
    }
}

export const computeExecCommand = async (cmd: string) => {
    console.log(`Executing command: ${cmd}`)
    let error
    let stdout, stderr
    try {
        ;({ stdout, stderr } = await execCommand(cmd))
    } catch (err) {
        console.error(err)
        error = err
        console.log(`Erro occured while executing command: ${cmd}`)
    }
    const data = { stdout, stderr }
    console.log(`Execution completed: \n${cmd}\n --> `, data)

    return [data, error]
}

exposeInMainWorld('spawn', spawnFn)
exposeInMainWorld('exec', computeExecCommand)
exposeInMainWorld('execSync', execSync)
