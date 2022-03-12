import { pyProgram, pythonscript, get, pyVersion, developerMode } from "../settings/svelteWritables";

export const dispatchEvent = (e, detail, eventName) => {
    const pyEventClosed = new CustomEvent(eventName,  { bubbles: false, detail })
    e?.target.dispatchEvent(pyEventClosed)
    console.info(eventName + " dispatched")
}

export default async function({ e = null, pyfile = "", args = {}, general = false, openShell = false } = {}) {
    
    let target;
    let dataFromPython = null;

    const outputFile = pathJoin(appInfo.temp, "FELion_GUI3", pyfile.split(".").at(-1) + "_data.json")
    if(fs.existsSync(outputFile)) fs.removeSync(outputFile)

    try {

        // if (!general) {
        //     target = e?.target
        //     target.classList.toggle("is-loading")
        // }
    
        // const PORT = 5050
        // const URL = `http://127.0.0.1:${PORT}/felionpy/compute`
        // const method =  'POST'
        // const headers =  {
        //     'Content-type': 'application/json',
        //     'Accept': 'application/json'
        // }

        // const body =  JSON.stringify({pyfile, args})
        // const response = await fetch(URL, {method, headers, body})
        
        // if(!response.ok) return Promise.resolve(null)

        // const {timeConsumed} = await response.json()
        // console.warn(timeConsumed)

        // if(!general) {
        //     if(!fs.existsSync(outputFile)) {
        //         console.warn(`${outputFile} file doesn't exists`)
        //         window.handleError(`${outputFile} file doesn't exists`)
        //     }
        //     dataFromPython = fs.readJsonSync(outputFile) || null
        //     console.table(dataFromPython)
        // }


        return new Promise(async (resolve) => {
            
            if(!get(pyVersion)) {
                window.handleError("Python is not valid. Fix it in Settings --> Configuration")
                return
            }
    
            console.info("Sending general arguments: ", args)
            window.createToast("Process Started")
            
            const sendArgs = [pyfile, JSON.stringify(args)]
            const mainPyFile = pathJoin(get(pythonscript), "main.py")

            const pyArgs = get(developerMode) ? [mainPyFile, ...sendArgs ] : sendArgs
            console.log(get(pyProgram), {pyArgs})
            
            const py = spawn( get(pyProgram), pyArgs, { detached: general, shell: openShell } )
            
            py.on("error", (err) => {
                window.handleError(err)
                return
            })
            
            if (!general) {
                target = e?.target
                target.classList.toggle("is-loading")
            }

            const logFile = pathJoin(appInfo.temp, "FELion_GUI3", pyfile + "_data.log")
            const loginfo = fs.createWriteStream(logFile)
        
            let error = ""
            let dataReceived = ""
            
            const outputFile = pathJoin(appInfo.temp, "FELion_GUI3", pyfile.split(".").at(-1) + "_data.json")
            if(fs.existsSync(outputFile)) fs.removeSync(outputFile)

            dispatchEvent(e, { py, pyfile }, "pyEvent")
            
            py.on("close", () => {

                dispatchEvent(e, { py, pyfile, dataReceived, error }, "pyEventClosed")
                if(!error) {
                
                    if(general) {resolve(dataReceived)}
                    else {

                        if(!fs.existsSync(outputFile)) {
                            console.warn(`${outputFile} file doesn't exists`)
                            window.handleError(`${outputFile} file doesn't exists`)
                            resolve(null)
                        }
                        
                        try {
                            const dataFromPython = fs.readJsonSync(outputFile)
                            console.table(dataFromPython)
                            resolve(dataFromPython)

                        } catch (error) {
                            console.warn(error)
                            window.handleError(error)
                            resolve(null)
                        }
                    }

                } else { 

                    resolve(null)
                    loginfo.write(`\n\n[ERROR OCCURED]\n${error}\n`)
                    loginfo.end()
                    window.handleError(error)
                }
                
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
    // finally {
    //     if(target?.classList.contains("is-loading")) {
    //         target.classList.remove("is-loading")
    //     }
    //     return Promise.resolve(dataFromPython)
    // }

}