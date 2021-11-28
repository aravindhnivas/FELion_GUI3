
import {pythonpath, pythonscript, pyVersion, get} from "./svelteWritables";

export async function resetPyConfig() {

    const mainLocation = appInfo.isPackaged ? appInfo.module : __dirname + "../"
    const unpackedLocation =  pathResolve(mainLocation, appInfo.isPackaged ? "../resources/app.asar.unpacked/" : "../" )
    
    db.set("pythonscript", pathResolve(unpackedLocation, "static/assets/python_files"))

    pythonscript.set(db.get("pythonscript"))
    const defaultPy = pathResolve(unpackedLocation, "python3/python")
    
    const [data, error] = await exec(`${defaultPy} -V`)
    if(error) return window.handleError(error)
    
    pyVersion.set(data.stdout.trim())

    db.set("pythonpath", defaultPy)
    pythonpath.set(defaultPy); 
    
    window.createToast("Location resetted", "warning")

}

export async function updatePyConfig(){

    const [data, error] = await exec(`${get(pythonpath)} -V`)
    if(error) return window.handleError(error)
    
    pyVersion.set(data.stdout.trim());
    window.createToast("Location updated", "success")

    db.set("pythonpath", get(pythonpath))
    db.set("pythonscript", get(pythonscript))
}

