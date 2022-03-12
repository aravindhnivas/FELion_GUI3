
import { pyProgram, pythonscript, get, pyVersion, pyServerReady, developerMode } from "../settings/svelteWritables";

export const dispatchEvent = (target, detail, eventName) => {
    const pyEventClosed = new CustomEvent(eventName,  { bubbles: false, detail })
    target?.dispatchEvent(pyEventClosed)
    console.info(eventName + " dispatched")
}

export default async function({
        e=null, button=null, general=false, pyfile, args,
        computepyfile="main", shell = false, detached = null

    })  {
    
    let outputFile;
    const target = button || e?.target;
    if(pyfile === "server") {pyServerReady.set(false)}

    if(!general) {
        outputFile = pathJoin(appInfo.temp, "FELion_GUI3", pyfile.split(".").at(-1) + "_data.json")
        if(fs.existsSync(outputFile)) {fs.removeSync(outputFile)}
        target?.classList.toggle("is-loading")
    } 

    return new Promise(async (resolve) => {
            
        if(!get(pyVersion)) {
            window.handleError("Python is not valid. Fix it in Settings --> Configuration")
            return
        }

        console.info("Sending general arguments: ", args)
        window.createToast("Process Started")
        
        const sendArgs = [pyfile, JSON.stringify(args)]
        const mainPyFile = pathJoin(get(pythonscript), computepyfile+".py")

        const pyArgs = get(developerMode) ? [mainPyFile, ...sendArgs ] : sendArgs
        console.log(get(pyProgram), {pyArgs})
        
        const opts = {detached: detached !== null ? detached : general, shell}
        const py = spawn(get(pyProgram), pyArgs, opts)
        
        py.on("error", (err) => {
            window.handleError(err)
            return
        })
        
        const logFile = pathJoin(appInfo.temp, "FELion_GUI3", pyfile + "_data.log")
        const loginfo = fs.createWriteStream(logFile)
    
        let error = ""
        let dataReceived = ""
        
        dispatchEvent(target, { py, pyfile }, "pyEvent")


        py.on("close", () => {

            if(pyfile === "server") {
                pyServerReady.set(false)
            }
            
            dispatchEvent(target, { py, pyfile, dataReceived, error }, "pyEventClosed")

            if(error) {
                resolve(null)
                loginfo.write(`\n\n[ERROR OCCURED]\n${error}\n`)
                loginfo.end()
                return console.error(error)
            }
            
            if(general) {return resolve(dataReceived)}

            if(!fs.existsSync(outputFile)) {
                console.warn(`${outputFile} file doesn't exists`)
                window.handleError(`${outputFile} file doesn't exists`)
                return resolve(null)
            }
            
            const dataFromPython = fs.readJsonSync(outputFile)
            resolve(dataFromPython)

            
            if(target?.classList.contains("is-loading")) {
                target.classList.remove("is-loading")
            }

            console.info("Process closed")

        })

        py.stderr.on("data", (err) => {
            if(pyfile === "server") {
                error = String.fromCharCode.apply(null, err)
            } else {error += String.fromCharCode.apply(null, err)}
            dispatchEvent(target, { py, pyfile, error }, "pyEventStderr")

        })

        py.stdout.on("data", (data) => {

            loginfo.write(data)

            if(pyfile === "server") {
                dataReceived = `${String.fromCharCode.apply(null, data)}\n`
            } else {dataReceived += `${String.fromCharCode.apply(null, data)}\n`}
            
            console.log(`Output from python: ${dataReceived}`)
            dispatchEvent(target, { py, pyfile, dataReceived }, "pyEventData")
        })

        if(pyfile === "server") {pyServerReady.set(true)}
    })
}