
import { pythonpath, pythonscript, get } from "../settings/svelteWritables";
// import { mainPreModal } from "../../svelteWritable";
const { exec } = require("child_process")
window.checkPython = function checkPython({ defaultPy } = {}) {

    if (!defaultPy) { defaultPy = get(pythonpath) }

    console.log("Python path checking \n", defaultPy)
    return new Promise((resolve, reject) => {
        exec(`${defaultPy} -V`, (err, stdout) => {
            if (err) { reject("Invalid python location"); window.createToast("Python location is not valid", "danger") }
            else { resolve(stdout.trim()) }

        })
    })
}

window.computePy_func = function computePy_func({ e = null, pyfile = "", args = "", general = false, openShell = false } = {}) {

    return new Promise((resolve, reject) => {

        let target;
        if (!general) {
            target = e.target
            target.classList.toggle("is-loading")

        }

        checkPython()

            .then(res => {
                console.log(res)
                if (general) {
                    console.log("Sending general arguments: ", args)
                    window.createToast("Process Started")
                    const py = spawn(
                        get(pythonpath), [path.join(get(pythonscript), pyfile), args], { detached: true, stdio: 'pipe', shell: openShell }

                    )

                    if (e) {


                        const pyEvent = new CustomEvent('pyEvent', { bubbles: false, detail: { py, pyfile } });
                        e.target.dispatchEvent(pyEvent)
                        console.log("pyEvent dispatched")
                    }

                    let error = "", error_occured_py=false;
                    let dataReceived="";
                    py.on("close", () => {

                        console.log("Closed")

                        if (error) {error_occured_py=true; reject(error); } 
                        if (e) {
                            const pyEventClosed = new CustomEvent('pyEventClosed', { bubbles: false, detail: { py, pyfile, dataReceived, error_occured_py } });
                            e.target.dispatchEvent(pyEventClosed)
                            console.log("pyEventClosed dispatched")
                        }
                        
                    })
                    py.stderr.on("data", (err) => { console.log(`Error Occured: ${err.toString()}`); error += err.toString() })
                    py.stdout.on("data", (data) => {

                        dataReceived += `${data.toString()}\n`
                        console.log(`Output from python: ${dataReceived}`)
                        if (e) {

                            const pyEventData = new CustomEvent('pyEventData', { bubbles: false, detail: { py, pyfile, dataReceived } });
                            e.target.dispatchEvent(pyEventData)

                            console.log("pyEventData dispatched")

                        }
                    })


                    py.unref()

                    py.ref()
                } else {

                    let py = null;
                    try { py = spawn(get(pythonpath), [path.resolve(get(pythonscript), pyfile), args]) }
                    catch (err) { reject("Error accessing python. Set python location properly in Settings\n" + err) }

                    if (e) {

                        const pyEvent = new CustomEvent('pyEvent', { bubbles: false, detail: { py, pyfile } });
                        e.target.dispatchEvent(pyEvent)
                        console.log("pyEvent dispatched")
                    }

                    window.createToast("Process Started")
                    let dataReceived = "";
                    py.stdout.on("data", data => {

                        console.log("Ouput from python")
                        dataReceived += data.toString("utf8")
                        console.log(dataReceived)

                        if (e) {

                            const pyEventData = new CustomEvent('pyEventData', { bubbles: false, detail: { py, pyfile, dataReceived } });
                            e.target.dispatchEvent(pyEventData)

                            console.log("pyEventData dispatched")

                        }
                    })
                    let error_occured_py = false, errContent = "";

                    py.stderr.on("data", err => {

                        errContent += err.toString()
                        console.error(errContent)

                        error_occured_py = true
                    });

                    py.on("close", () => {
                        if (!error_occured_py) {
                            const dataFile = path.basename(pyfile).split(".")[0]

                            const outputFile = path.join(get(pythonscript), "local", dataFile + "_data.json")

                            if (!fs.existsSync(outputFile)) {
                                return reject(`${outputFile} doesn't exist.`)
                            }
                            let dataFromPython = fs.readFileSync(outputFile)



                            window.dataFromPython = dataFromPython = JSON.parse(dataFromPython.toString("utf-8"))
                            console.log(dataFromPython)
                            resolve(dataFromPython)
                        
                        } else { reject(errContent);  }
                        if (e) {
                            const pyEventClosed = new CustomEvent('pyEventClosed', { bubbles: false, detail: { py, pyfile, dataReceived, error_occured_py } });


                            e.target.dispatchEvent(pyEventClosed)

                            console.log("pyEventClosed dispatched")
                        }

                        target.classList.toggle("is-loading")
                        console.log("Process closed")
                    })

                }
            }).catch(err => { reject(err.stack); })
        // .finally(()=>{if (!general) { target.classList.toggle("is-loading") }})

    })

}