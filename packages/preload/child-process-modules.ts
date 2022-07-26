import { exposeInMainWorld } from './exposeInMainWorld'
import { promisify } from 'util'
import * as child from 'child_process';
// import { spawn, exec, execSync } from 'child_process'
const execSync = child.execSync
export { execSync }
const execCommand = promisify(child.exec)

type SpawnPick = Pick<child.ChildProcessWithoutNullStreams, "pid" | "killed" | "ref" | "unref" | "kill" | "on">
type SpawnReturnType = SpawnPick & {
    stdout: {on: (event: 'data', listener: (data: string) => void) => void}
    stderr: {on: (event: 'data', listener: (data: string) => void) => void}
}

export function spawnFn(cmd: string, args: readonly string[] = [], opts?: child.SpawnOptionsWithoutStdio | undefined): SpawnReturnType {

    const process = child.spawn(cmd, args, opts);
    console.log(`Spawned child pid: ${process.pid}`);
    
    return {
        pid: process.pid,
        killed: process.killed,
        ref() {
            return process.ref();
        },
        unref() {
            return process.unref();
        },
        kill(signal = 2) {
            return process.kill(signal);
        },
        on: (event, listener) => process.on(event, listener),
        stdout: { 
            on: (event, listener) => process.stdout.on(event, (data) => {
                const str = String.fromCharCode.apply(null, data);
                listener(str);
            })
         },
        stderr: { 
            on: (event, listener) => process.stderr.on(event, (data) => {
                const str = String.fromCharCode.apply(null, data);
                listener(str);
            })
         },
    };
}

export async function computeExecCommand(cmd: string) {
    
    console.log(`Executing command: ${cmd}`);
    
    let error: Error | undefined;
    let stdout: string = "";
    let stderr: string = "";

    try {
        ;({ stdout, stderr } = await execCommand(cmd));
    
    } catch (err) {
        error = <Error>err;
        console.log(`Erro occured while executing command: ${cmd}`);
    }
    const data = { stdout, stderr };
    console.log(`Execution completed: \n${cmd}\n --> `, data);
    return [data, error];
}

exposeInMainWorld('spawn', spawnFn)
exposeInMainWorld('exec', computeExecCommand)
exposeInMainWorld('execSync', execSync)
