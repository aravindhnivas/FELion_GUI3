
import { pythonpath, pythonscript, get } from "../settings/svelteWritables";
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
                    let py = spawn(
                        get(pythonpath), [path.join(get(pythonscript), pyfile), args], { detached: true, stdio: 'pipe', shell: openShell }

                    )

                    // target.classList.toggle("is-loading")

                    py.on("close", () => { console.log("Closed") })
                    py.stderr.on("data", (err) => { console.log(`Error Occured: ${err.toString()}`); reject(err.toString()) })
                    py.stdout.on("data", (data) => { console.log(`Output from python: ${data.toString()}`) })


                    py.unref()

                    py.ref()
                } else {

                    let py = null;
                    try { py = spawn(get(pythonpath), [path.resolve(get(pythonscript), pyfile), args]) }
                    catch (err) { reject("Error accessing python. Set python location properly in Settings\n" + err) }

                    window.createToast("Process Started")
                    py.stdout.on("data", data => {

                        console.log("Ouput from python")
                        let dataReceived = data.toString("utf8")
                        console.log(dataReceived)
                    })

                    let error_occured_py = false, errContent="";

                    py.stderr.on("data", err => {
                        
                        errContent = err.toString()
                        console.error(errContent)
                        reject(errContent)
                        error_occured_py = true
                    });

                    py.on("close", (errContent) => {
                        if (!error_occured_py) {
                            let dataFromPython = fs.readFileSync(path.join(get(pythonscript), "data.json"))
                            window.dataFromPython = dataFromPython = JSON.parse(dataFromPython.toString("utf-8"))
                            console.log(dataFromPython)
                            resolve(dataFromPython)

                        }
                        target.classList.toggle("is-loading")

                        console.log("Process closed")

                    })

                }

            }).catch(err => { reject(err.stack); if (!general) { target.classList.toggle("is-loading") } })
    })

}