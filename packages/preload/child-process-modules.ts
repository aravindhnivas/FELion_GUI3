import { exposeInMainWorld } from './exposeInMainWorld'
import { promisify } from 'util'
import * as child from 'child_process';
import { tryF } from 'ts-try';
const execSync = child.execSync
export { execSync }

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

export async function exec(cmd: string) {
    console.log(`Executing command: ${cmd}`);
    const fn = promisify(child.exec);
    const data = await tryF(fn(cmd));
    return data
}

exposeInMainWorld('spawn', spawnFn)
exposeInMainWorld('exec', exec)
exposeInMainWorld('execSync', execSync)
