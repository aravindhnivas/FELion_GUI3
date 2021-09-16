
import {pythonpath, pythonscript, pyVersion, get} from "./svelteWritables";

// Renaming old python path (if exists)
function renamePy() {

    console.log("Checking for python old path")

    const oldPath = pathResolve(__dirname, "../python3.7")
    const newPath = pathResolve(__dirname, "../python3")

    if (existsSync(oldPath)) {

        rename(oldPath, newPath, function(err) {

            if (err) throw console.log(err)
            
            console.log("Successfully renamed the directory.")
        })
    }
}
renamePy()

export function resetPyConfig() {


    db.set("pythonscript", pathResolve(__dirname, "assets/python_files"))
    pythonscript.set(db.get("pythonscript"))
    const defaultPy = pathResolve(__dirname, "../python3/python")

    db.set("pythonpath", defaultPy)

    checkPython({defaultPy})
        .then((version)=>{
    
            pyVersion.set(version);
            pythonpath.set(db.get("pythonpath")); 
            window.createToast("Location resetted", "warning")
    
        })
    
}


export function updatePyConfig(){

    checkPython()
        .then(version=>{
    
            pyVersion.set(version);
            db.set("pythonpath", get(pythonpath))

            window.createToast("Location updated", "success")
        })

        db.set("pythonscript", get(pythonscript))
}