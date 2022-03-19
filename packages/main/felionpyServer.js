import { ipcMain } from 'electron'
import path from "path"
import { promisify } from 'util'
import { spawn, exec  } from 'child_process'
import {ROOT_DIR} from "./definedEnv"
import getPort from 'get-port';
import Store from 'electron-store'

const env = import.meta.env;
const execCommand = promisify(exec);

const getCurrentDevStatus = () => {

    const db = new Store({name: "db"})
    
    if(!db.has("developerMode")) {
        db.set("developerMode", env.DEV)
    }
    const developerMode = db.get("developerMode")
    const pythonscript = db.get("pythonscript") || path.join(ROOT_DIR, "resources/python_files")
    const pythonpath = db.get("pythonpath") || path.join(ROOT_DIR, "resources/python_files")
    const pyProgram = developerMode ? pythonpath : path.join(ROOT_DIR, "resources/felionpy/felionpy")
    const mainpyfile = developerMode ? path.join(pythonscript, "main.py") : ""

    return {db, developerMode, pyProgram, mainpyfile}

}
let pyVersion;

export async function getPyVersion() {
    
    try{

        const {pyProgram, mainpyfile} = getCurrentDevStatus()
        const pyfile = "getVersion"

        const command = `${pyProgram} ${mainpyfile} ${pyfile} {} `
        const {stdout} = await execCommand(command)

        const [version] = stdout?.split("\n")?.filter?.(line => line.includes("Python")) || [""]
        pyVersion = version?.trim() || ""
        console.log({stdout, version})
        // webContents?.send('db:update', {key: "pyVersion", value: pyVersion})
        return Promise.resolve(pyVersion)

    } catch (error) {
        
        console.error("could not get python version")
        console.error(error)

        return Promise.resolve(false)
    }
}


let py;
let controller;
export async function startServer(webContents) {

    const {db, developerMode, pyProgram, mainpyfile} = getCurrentDevStatus()
    const serverDebug = db.get("serverDebug") ?? false
    const dbPORT = db.get("pyServerPORT")
    const availablePORT = await getPort({port: [5050, 5353, 3000, dbPORT]})

    console.log({dbPORT, availablePORT})

    webContents?.send('db:update', {key: "pyServerPORT", value: availablePORT})
    console.info("starting felionpy server at port: ", availablePORT)
    
    return new Promise(async (resolve, reject)=>{

    
        webContents?.send('db:update', {key: "pyServerReady", value: false})
        pyVersion ||= db.get("pyVersion")
        
        if(!pyVersion) {

            pyVersion = await getPyVersion()
            if(!pyVersion) {
                console.error("Python is not valid. Fix it in Settings --> Configuration")
                reject("Python is not valid. Fix it in Settings --> Configuration")
                return
            }
            webContents?.send('db:update', {key: "pyVersion", value: pyVersion})
        }

        console.log(pyVersion)

        const pyfile = "server"
        const sendArgs = [pyfile, JSON.stringify({port: availablePORT, debug: serverDebug})]
        
        const pyArgs = developerMode ? [mainpyfile, ...sendArgs] : sendArgs
        console.warn({pyProgram, pyArgs})

        const opts = {}
        
        try {
            
            py = spawn(pyProgram, pyArgs, opts)

            py.on("error", (error) => {

                webContents?.send('db:update', {key: "pyServerReady", value: false})
                console.error(error)
                reject(error)
            })

            py.on("spawn", () => {
                db.set("pyServerReady", true)
                webContents?.send('db:update', {key: "pyServerReady", value: true})
                console.info("pyServerReady", db.get("pyServerReady"))

                console.log("server ready")
            })

            py.on("exit", () => {

                db.set("pyServerReady", false)
                webContents?.send('db:update', {key: "pyServerReady", value: false})
                console.log("server closed")
            
            })
            
            py.stderr.on("data", (err) => {
                const stderr = String.fromCharCode.apply(null, err)
                console.warn(stderr)
            })

            py.stdout.on("data", (data) => {
                const stdout = String.fromCharCode.apply(null, data)
                console.info(stdout)
            })

        } catch (error) {

            console.error(error)
            webContents?.send('db:update', {key: "pyServerReady", value: false})
            reject(error); 

        }
    })
}

ipcMain.on("stopServer", (event, args) => py?.kill?.())
