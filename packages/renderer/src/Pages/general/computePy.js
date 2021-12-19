import { pythonpath, pythonscript, get, pyVersion, developerMode } from "../settings/svelteWritables";

const dispatchEvent = (e, detail, eventName) => {
    const pyEventClosed = new CustomEvent(eventName,  { bubbles: false, detail })
    e?.target.dispatchEvent(pyEventClosed)
    console.info(eventName + " dispatched")
}

window.computePy_func = async ({
    e = null, pyfile = "", args = "",
    general = false, openShell = false 
    } = {}) => {
    
    let target;
    try {

        if(get(developerMode) && !get(pyVersion)) {
            window.handleError("Python is not valid. Fix it in Settings --> Configuration")
            return
        }

        console.info("Sending general arguments: ", args)
        window.createToast("Process Started")
        
        const pyProgram = get(developerMode) ? get(pythonpath) : pathJoin(ROOT_DIR, "resources/felionpy/felionpy")
        const pyArgs = get(developerMode) ? [pathJoin(get(pythonscript), "main.py"), pyfile, args ] : [pyfile, args]
        console.log({pyArgs})
        const py = spawn( pyProgram, pyArgs, { detached: general, shell: openShell } )

        py.on("error", (err) => {
            window.handleError(err)
            return
        })

        
        if (!general) {
            target = e?.target
            target.classList.toggle("is-loading")
        }


        return new Promise(async (resolve) => {
            const logFile = pathJoin(appInfo.temp, "FELion_GUI3", pyfile + "_data.log")
            const loginfo = fs.createWriteStream(logFile)
        
            let error = ""
            let dataReceived = ""
            
            const outputFile = pathJoin(appInfo.temp, "FELion_GUI3", pyfile + "_data.json")
            if(fs.existsSync(outputFile)) fs.removeSync(outputFile)

            dispatchEvent(e, { py, pyfile }, "pyEvent")
            
            py.on("close", () => {

                dispatchEvent(e, { py, pyfile, dataReceived, error }, "pyEventClosed")
                
                if(!error) {
                
                    if(general) {resolve(dataReceived)}

                    else {
                        if(!fs.existsSync(outputFile)) {
                            window.handleError(`${outputFile} file doesn't exists`)
                            return resolve(null)
                        }

                        const dataFromPython = fs.readJsonSync(outputFile)
                        
                        console.table(dataFromPython)
                        resolve(dataFromPython)
                    }

                } else { 
                    
                    resolve(null)
                    window.handleError(error)
                    
                    loginfo.write(`\n\n[ERROR OCCURED]\n${error}\n`)
                }
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

    }
}
