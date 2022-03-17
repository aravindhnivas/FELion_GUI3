
// import { contextBridge } from 'electron'
// import path from "path"
// import logger from "electron-log"
// import {db} from "./jsondb-modules"
// import { spawn } from 'child_process'
// import { killer } from 'cross-port-killer';
// import { getPortId } from './mangeServer';
// import { computeExecCommand as exec } from './child-process-modules'
// import {pyVersion, developerMode, pythonscript, pyProgram, get} from "./stores"

// export async function getPyVersion() {
    
//     db.set("pyVersion", "")
//     const pyfile = "getVersion"
//     const pyArgs = get(developerMode) ? path.join(get(pythonscript), "main.py") : ""

//     const command = `${get(pyProgram)} ${pyArgs} ${pyfile} {} `
//     const [{stdout}, error] = await exec(command)
//     if(error) return Promise.reject(error)

//     const [version] = stdout?.split("\n").filter?.(line => line.includes("Python")) || [""]
//     pyVersion.set(version?.trim() || "")
//     db.set("pyVersion", get(pyVersion))
//     console.log({stdout, version})

//     if(get(pyVersion)) return Promise.resolve(get(pyVersion))
// }

// export async function startServer() {

//     if(!db.has("serverDebug")) db.set("serverDebug", false)
        
//     const port = db.get("pyServerPORT")
//     const debug = db.get("serverDebug")

//     const pids = await getPortId(port)
//     if(pids) {await killer.killByPid(pids)}

//     logger.info("starting delionpy server")
//     return new Promise(async (resolve, reject)=>{

//         db.set("pyServerReady", false)
//         await getPyVersion()

//         if(!get(pyVersion)) {
//             reject("Python is not valid. Fix it in Settings --> Configuration")
//             return
//         }

//         console.log(get(pyVersion))
//         const pyfile = "server"

        
        
//         const sendArgs = [pyfile, JSON.stringify({port, debug})]
//         const mainPyFile = path.join(get(pythonscript), "main.py")

//         const pyArgs = get(developerMode) ? [mainPyFile, ...sendArgs ] : sendArgs
//         console.warn(get(pyProgram), pyArgs)

//         const opts = {detached: true}
        
//         try {
//             const py = spawn(get(pyProgram), pyArgs, opts)
//             py.unref()

//             py.on("error", (error) => {
//                 db.set("pyServerReady", false);
//                 logger.errror(error)
//                 reject(error)
//             })
//             py.on("close", () => db.set("pyServerReady", false))
//             py.stderr.on("data", (err) => {
//                 const stderr = String.fromCharCode.apply(null, err)
//                 logger.warn(stderr)

//             })
//             py.stdout.on("data", (data) => {
//                 const stdout = String.fromCharCode.apply(null, data)
//                 logger.info(stdout)

//             })
            
//             db.set("pyServerReady", true)
//             resolve("server ready")

//         } catch (error) {
//             logger.errror(error)
//             reject(error); db.set("pyServerReady", false)
//         }
//     })
// }

// contextBridge.exposeInMainWorld("startServer", startServer)
