
import {pythonpath, pythonscript, pyVersion, get} from "./svelteWritables";
const {exec} = require("child_process")

// Renaming old python path (if exists)
function renamePy() {

    console.log("Checking for python old path")

    const oldPath = path.resolve(__dirname, "../python3.7")
    const newPath = path.resolve(__dirname, "../python3")

    if (fs.existsSync(oldPath)) {

        fs.rename(oldPath, newPath, function(err) {

            if (err) throw console.log(err)
            
            console.log("Successfully renamed the directory.")
        })
    }
}
renamePy()

export function checkPython({defaultPy}={}){

    if(!defaultPy) {defaultPy = get(pythonpath)}

    console.log("Python path checking \n", defaultPy)
    return new Promise((resolve, reject)=>{
        exec(`${defaultPy} -V`, (err, stdout)=>{
            if(err) {reject("Invalid"); createToast("Python location is not valid", "danger")}
            else {resolve(stdout.trim())}
        })
    })
}

export function resetPyConfig() {

    localStorage["pythonscript"] = path.resolve(__dirname, "assets/python_files")
    pythonscript.set(localStorage["pythonscript"])
    const defaultPy = path.resolve(__dirname, "../python3/python")


    localStorage["pythonpath"] = defaultPy

    checkPython({defaultPy})
        .then((version)=>{
    
            pyVersion.set(version);
            pythonpath.set(localStorage["pythonpath"]); 
            createToast("Location resetted", "warning")
    
        })
    
}


export function updatePyConfig(){
    checkPython()
        .then(version=>{
            pyVersion.set(version);
            localStorage["pythonpath"] = get(pythonpath)
            createToast("Location updated", "success")
        })
        localStorage["pythonscript"] = get(pythonscript)
        
}