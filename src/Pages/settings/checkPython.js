
import {pythonpath, pythonscript, pyVersion, get} from "./svelteWritables";

export function resetPyConfig() {
    const mainLocation = appInfo.isPackaged ? appInfo.module : __dirname + "../"
    const unpackedLocation =  pathResolve(mainLocation, appInfo.isPackaged ? "../resources/app.asar.unpacked/" : "../" )
    db.set("pythonscript", pathResolve(unpackedLocation, "static/assets/python_files"))

    pythonscript.set(db.get("pythonscript"))
    const defaultPy = pathResolve(unpackedLocation, "python3/python")
    db.set("pythonpath", defaultPy)


    checkPython({defaultPy})
        .then(({stdout})=>{
            pyVersion.set(stdout.trim());
            pythonpath.set(db.get("pythonpath")); 
            window.createToast("Location resetted", "warning")
    
    
        }).catch(handleError)
    
}

export function updatePyConfig(){

    checkPython()
        .then(({stdout})=>{
            pyVersion.set(stdout.trim());
            db.set("pythonpath", get(pythonpath))
            window.createToast("Location updated", "success")
        }).catch(handleError)
        db.set("pythonscript", get(pythonscript))
}