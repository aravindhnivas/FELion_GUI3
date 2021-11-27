
import { pythonpath, pythonscript, get } from "../settings/svelteWritables";

window.checkPython = function checkPython({ defaultPy } = {}) {

    if (!defaultPy) { defaultPy = get(pythonpath) }
    console.log("Python path checking \n", defaultPy)
    
    return execFile(`${defaultPy}`, ["-V"])

}


const dispatchEvent = (e, detail, eventName) => {
    const pyEventClosed = new CustomEvent(eventName,  { bubbles: false, detail })
    e?.target.dispatchEvent(pyEventClosed)
    console.info(eventName + " dispatched")

}

window.computePy_func = (
        { 
            e = null,
            pyfile = "",
            args = "",
            general = false,
            openShell = false 
        } = {}
    ) => {
    
    return new Promise(async (resolve, reject) => {

        let target;
        if (!general) {
            target = e.target
            target.classList.toggle("is-loading")
        }

        try {
            
            await checkPython()
            console.info("Sending general arguments: ", args)
            window.createToast("Process Started")

            const py = spawn(
                get(pythonpath), 
                [pathJoin(get(pythonscript), pyfile), args], 
                { detached: general, shell: openShell }
            )

            dispatchEvent(e, { py, pyfile }, "pyEvent")
            
            let error = ""
            let dataReceived=""

            py.on("close", () => {
                dispatchEvent(e, { py, pyfile, dataReceived, error }, "pyEventClosed")
                if(!error) {
                    
                    if(general) {
                        resolve(dataReceived)
                    } else {
                        const dataFile = basename(pyfile).split(".")[0]
                        const outputFile = pathJoin(appInfo.temp, "FELion_GUI3", dataFile + "_data.json")
                        const dataFromPython = fs.readJsonSync(outputFile)
                        console.table(dataFromPython)
                        resolve(dataFromPython)
                    }
                }

                if(target) {
                    target.classList.toggle("is-loading")
                    console.info("Process closed")
                }
                
            })

            py.stderr.on("data", (err) => { 
                error += String.fromCharCode.apply(null, err)
                // console.log(`Error Ocurred: ${error}`); 
                dispatchEvent(e, { py, pyfile, dataReceived }, "pyEventData")
            })

            py.stdout.on("data", (data) => {
                dataReceived += `${String.fromCharCode.apply(null, data)}\n`
                console.log(`Output from python: ${dataReceived}`)
                dispatchEvent(e, { py, pyfile, dataReceived }, "pyEventData")
            })

            if(general) {

                py.unref()
                py.ref()
            }
            
        } catch (error) {
            reject(error)
            window.handleError(error)
        }
    })

}