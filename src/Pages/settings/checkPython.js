
import {pythonpath, pythonscript, pyVersion, get} from "./svelteWritables";

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