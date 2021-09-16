
import { pythonpath, pythonscript, get } from "../settings/svelteWritables";
// import { mainPreModal } from "../../svelteWritable";
// import { spawn, exec } from "child_process"
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
                        get(pythonpath), [pathJoin(get(pythonscript), pyfile), args], { detached: true, stdio: 'pipe', shell: openShell }

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

                        if (error) {error_occured_py=true; reject(error); console.log("error Ocurred: ", error) } 
                        if (e) {
                            const pyEventClosed = new CustomEvent('pyEventClosed', { bubbles: false, detail: { py, pyfile, dataReceived, error_occured_py } });
                            e.target.dispatchEvent(pyEventClosed)
                            console.log("pyEventClosed dispatched")
                        }
                    })
                    py.stderr.on("data", (err) => { 
                        error = String.fromCharCode.apply(null, err)
                        console.log(`Error Ocurred: ${error}`); 
                    })

                    py.stdout.on("data", (data) => {

                        // dataReceived += `${data.toString()}\n`
                        dataReceived += `${String.fromCharCode.apply(null, data)}\n`
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
                    try { py = spawn(get(pythonpath), [pathResolve(get(pythonscript), pyfile), args]) }
                    catch (err) { reject("Error accessing python. Set python location properly in Settings\n" + err) }

                    if (e) {

                        const pyEvent = new CustomEvent('pyEvent', { bubbles: false, detail: { py, pyfile } });
                        e.target.dispatchEvent(pyEvent)
                        console.log("pyEvent dispatched")
                    }

                    window.createToast("Process Started")
                    let dataReceived = "";
                    py.stdout.on("data", data => {
                        // console.log(typeof data, data)
                        console.log("Ouput from python")
                        // dataReceived += data.toString("utf8")
                        dataReceived += String.fromCharCode.apply(null, data)
                        console.log(dataReceived)

                        if (e) {

                            const pyEventData = new CustomEvent('pyEventData', { bubbles: false, detail: { py, pyfile, dataReceived } });
                            e.target.dispatchEvent(pyEventData)

                            console.log("pyEventData dispatched")

                        }
                    })

                    let errContent = "";
                    let error_occured_py = false;
                    py.stderr.on("data", err => {
                        errContent += String.fromCharCode.apply(null, err)
                        error_occured_py = true
                    });

                    py.on("close", () => {
                        if (!error_occured_py) {
                            const dataFile = basename(pyfile).split(".")[0]
                            const outputFile = pathJoin(get(pythonscript), "local", dataFile + "_data.json")

                            if (!existsSync(outputFile)) {
                                return reject(`${outputFile} doesn't exist.`)
                            }
                            let dataFromPython = readFileSync(outputFile)

                            window.dataFromPython = dataFromPython = JSON.parse(dataFromPython)
                            console.log(dataFromPython)


                            resolve(dataFromPython)
                        
                        } else { reject(errContent);  console.log(errContent)}
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

    })
}