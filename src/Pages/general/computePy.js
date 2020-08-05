
import {pythonpath, get} from "../settings/svelteWritables";
const {exec} = require("child_process")
window.checkPython = function checkPython({defaultPy}={}){

    if(!defaultPy) {defaultPy = get(pythonpath)}

    console.log("Python path checking \n", defaultPy)
    return new Promise((resolve, reject)=>{
        exec(`${defaultPy} -V`, (err, stdout)=>{
            if(err) {reject("Invalid python location"); createToast("Python location is not valid", "danger")}
            else {resolve(stdout.trim())}
        })
    })
}

window.computePy_func = function computePy_func({e=null, pyfile="", args="", general=false, openShell=false}={}){


    return new Promise((resolve, reject)=>{


        checkPython().then(res=>{
            console.log(res)
            if(general){
                console.log("Sending general arguments: ", args)
                
                createToast("Process Started")

                let py = spawn(

                    localStorage["pythonpath"], [path.join(localStorage["pythonscript"], pyfile), args], { detached: true, stdio: 'pipe', shell: openShell }
        
                )
        
                py.on("close", ()=>{ console.log("Closed") })
                
                py.stderr.on("data", (err)=>{ console.log(`Error Occured: ${err.toString()}`); reject(err.toString()) })
                
                py.stdout.on("data", (data)=>{ console.log(`Output from python: ${data.toString()}`)  })
                py.unref()
                py.ref()
            } else {

                let py=null;
            
                try {py = spawn( localStorage["pythonpath"], [path.resolve(localStorage["pythonscript"], pyfile), args] )}
                catch (err) { reject("Error accessing python. Set python location properly in Settings\n"+err) }

                let target = e.target
                target.classList.toggle("is-loading")

                createToast("Process Started")
            
                py.stdout.on("data", data => {
            
                    console.log("Ouput from python")
            
                    let dataReceived = data.toString("utf8")
                    console.log(dataReceived)
                })
            
                let error_occured_py = false;
                py.stderr.on("data", err => {
                    reject(err)
                    error_occured_py = true
                });
            
                py.on("close", ()=>{
                    if(!error_occured_py) {
                        let dataFromPython = fs.readFileSync(path.join(localStorage["pythonscript"], "data.json"))

                        window.dataFromPython = dataFromPython = JSON.parse(dataFromPython.toString("utf-8"))
                        console.log(dataFromPython)

                        resolve(dataFromPython)
                    }
                    console.log("Process closed")
                    
                    target.classList.toggle("is-loading")
            
                })
            }
        }).catch(err=>{console.log(err)})

    })
    
}