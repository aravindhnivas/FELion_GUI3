
import { pythonpath, pythonscript, get, pyVersion, developerMode } from "../settings/svelteWritables";

const dispatchEvent = (e, detail, eventName) => {
    const pyEventClosed = new CustomEvent(eventName,  { bubbles: false, detail })
    e?.target.dispatchEvent(pyEventClosed)
    console.info(eventName + " dispatched")

}




window.computePy_func = async ({
        e = null,
        pyfile = "",
        args = "",
        general = false,
        openShell = false 
    } = {}) => {
    
    try {
        if(get(developerMode) && !get(pyVersion)) {
            const error = "Python is not valid. Fix it in Settings --> Configuration"
            return Promise.reject(error)
        }

        console.info("Sending general arguments: ", args)
        window.createToast("Process Started")
        const pyProgram = get(developerMode) ? get(pythonpath) : pathJoin(ROOT_DIR, "resources/felionpy/felionpy")
        const pyArgs = get(developerMode) ? [pathJoin(get(pythonscript), "main.py"), pyfile, args ] : [pyfile, args]
        const py = spawn( pyProgram, pyArgs, { detached: general, shell: openShell } )

        let error = ""
        let dataReceived=""
        
        const dataFile = basename(pyfile).split(".")[0]
        const logFile = pathJoin(appInfo.temp, "FELion_GUI3", dataFile + "_data.log")

        const loginfo = fs.createWriteStream(logFile)
        
        py.on("error", (err) => {
            error = err
            return Promise.reject(err)
        })

        let target;
        if (!general) {
            target = e.target
            target.classList.toggle("is-loading")
        }
        return new Promise(async (resolve, reject) => {
        
            
            
            const outputFile = pathJoin(appInfo.temp, "FELion_GUI3", dataFile + "_data.json")
            if(fs.existsSync(outputFile)) fs.removeSync(outputFile)

            dispatchEvent(e, { py, pyfile }, "pyEvent")
            
            py.on("close", () => {
                dispatchEvent(e, { py, pyfile, dataReceived, error }, "pyEventClosed")
                
                if(!error) {
                    
                    if(general) {
                        resolve(dataReceived)
                    } else {
                        const dataFromPython = fs.readJsonSync(outputFile)
                        if(!fs.existsSync(outputFile)) return reject(`${outputFile} file doesn't exists`)
                        console.table(dataFromPython)
                        resolve(dataFromPython)
                    }
                } else { reject(error); loginfo.write(`\n\n[ERROR OCCURED]\n${error}\n`) }
                loginfo.end()
                if(target?.classList.contains("is-loading")) {
                    target.classList.remove("is-loading")
                }
                console.info("Process closed")
            })

            py.stderr.on("data", (err) => {
                error += String.fromCharCode.apply(null, err)
                dispatchEvent(e, { py, pyfile, dataReceived }, "pyEventData")
            })

            py.stdout.on("data", (data) => {
                loginfo.write(data)
                dataReceived += `${String.fromCharCode.apply(null, data)}\n`
                console.log(`Output from python: ${dataReceived}`)
                dispatchEvent(e, { py, pyfile, dataReceived }, "pyEventData")
            })

            if(general) {
                py.unref()
                py.ref()
            }
        })

    } catch (error) {
        window.handleError(error)
        if(target?.classList.contains("is-loading")) {
            target.classList.remove("is-loading")
        }
        return Promise.reject(error)
    }

}

