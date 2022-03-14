
import path from "path"
import {db} from "./jsondb-modules"
import { spawn } from 'child_process'
import { computeExecCommand as exec } from './child-process-modules'
import {pyVersion, developerMode, pythonscript, pyProgram, get} from "./stores"

export async function getPyVersion() {
    
    db.set("pyVersion", "")
    const pyfile = "getVersion"
    const pyArgs = get(developerMode) ? path.join(get(pythonscript), "main.py") : ""

    const command = `${get(pyProgram)} ${pyArgs} ${pyfile} {} `
    const [{stdout}, error] = await exec(command)
    if(error) return Promise.reject(error)

    const [version] = stdout?.split("\n").filter?.(line => line.includes("Python")) || [""]
    pyVersion.set(version?.trim() || "")
    db.set("pyVersion", get(pyVersion))
    console.log({stdout, version})

    if(get(pyVersion)) return Promise.resolve(get(pyVersion))
}

export async function startServer() {
    return new Promise(async (resolve, reject)=>{

        db.set("pyServerReady", false)
        await getPyVersion()

        if(!get(pyVersion)) {
            reject("Python is not valid. Fix it in Settings --> Configuration")
            return
        }

        console.log(get(pyVersion))
        const pyfile = "server"

        const sendArgs = [pyfile, JSON.stringify({port: db.get("pyServerPORT"), debug: false})]
        const mainPyFile = path.join(get(pythonscript), "main.py")

        const pyArgs = get(developerMode) ? [mainPyFile, ...sendArgs ] : sendArgs
        console.warn(get(pyProgram), pyArgs)

        const opts = {}
        
        try {
            const py = spawn(get(pyProgram), pyArgs, opts)
            py.on("error", (err) => {
                db.set("pyServerReady", false); 
                console.error(err)
                reject(error)
            })
            py.on("close", () => db.set("pyServerReady", false))
            py.stderr.on("data", (err) => console.warn(String.fromCharCode.apply(null, err)))
            py.stdout.on("data", (data) => console.log(`Output from python: ${String.fromCharCode.apply(null, data)}`))

            db.set("pyServerReady", true)
            resolve("server ready")

        } catch (error) {reject(error); db.set("pyServerReady", false)}
    })
}
