
import {pythonpath, pythonscript, pyVersion, get} from "./svelteWritables";

export async function resetPyConfig() {

    const pyPath = pathJoin(ROOT_DIR, "python3/python")
    const pyScriptPath = pathJoin(__dirname, "assets/python_files")

    db.set("pythonscript", pyScriptPath)
    pythonscript.set(db.get("pythonscript"))


    const [data, error] = await exec(`${pyPath} -V`)
    if(error) return window.handleError(error)
    
    pyVersion.set(data.stdout.trim())

    db.set("pythonpath", pyPath)
    pythonpath.set(pyPath); 
    
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

