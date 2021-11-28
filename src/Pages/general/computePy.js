
import { pythonpath, pythonscript, get, pyVersion } from "../settings/svelteWritables";

const dispatchEvent = (e, detail, eventName) => {
    const pyEventClosed = new CustomEvent(eventName,  { bubbles: false, detail })

    e?.target.dispatchEvent(pyEventClosed)
    console.info(eventName + " dispatched")
}

window.computePy_func = async (
        { 
            e = null,
            pyfile = "",
            args = "",
            general = false,
            openShell = false 
        } = {}
    ) => {

    if(!get(pyVersion)) {
        const error = "Python is not valid. Fix it in Settings --> Configuration"
        return Promise.reject(error)
    }

    let target;
    if (!general) {
        target = e.target
        target.classList.toggle("is-loading")
    }
    return new Promise(async (resolve, reject) => {
        try {
            console.info("Sending general arguments: ", args)
            window.createToast("Process Started")

            const py = spawn(
                get(pythonpath), 
                [pathJoin(get(pythonscript), pyfile), args], 
                { detached: general, shell: openShell }
            )

            const dataFile = basename(pyfile).split(".")[0]
            const outputFile = pathJoin(appInfo.temp, "FELion_GUI3", dataFile + "_data.json")
            if(fs.existsSync(outputFile)) fs.removeSync(outputFile)

            const logFile = pathJoin(appInfo.temp, "FELion_GUI3", dataFile + "_data.log")
            const loginfo = fs.createWriteStream(logFile)

            dispatchEvent(e, { py, pyfile }, "pyEvent")
            
            let error = ""
            let dataReceived=""

            py.on("close", () => {
                dispatchEvent(e, { py, pyfile, dataReceived, error }, "pyEventClosed")
                
                if(!error) {
                    
                    if(general) {
                        resolve(dataReceived)
                    } else {
                        const dataFromPython = fs.readJsonSync(outputFile)
                        console.table(dataFromPython)
                        resolve(dataFromPython)
                    }
                } else { reject(error); loginfo.write(`\n\n[ERROR OCCURED]\n${error}\n`) }
                loginfo.end()
                target?.classList.toggle("is-loading")
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
            
        } catch (error) {
            reject(error)
            window.handleError(error)
            target?.classList.toggle("is-loading")
        }
    })

}
