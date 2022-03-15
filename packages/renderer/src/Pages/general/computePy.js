import computefromServer from "./computefromServer"
import {pyVersion, pyServerReady, get} from "../settings/svelteWritables"

export default async function({
        e = null, target=null, pyfile = "",
        args = {}, general = false, 
    } = {}) {

    target ||= e?.target
    let dataFromPython = null;
    
    try {

        if(!get(pyServerReady)) {
            window.handleError("Python server is not ready. Fix it in Settings --> Configuration")
            return Promise.resolve(null)
        }
    
        if(!get(pyVersion)) {
            window.handleError("Python could not be loaded. Check in Settings --> Configuration")
            return Promise.resolve(null)
        }
        
        dataFromPython = await computefromServer({target, general, pyfile, args})
    } 
    catch (error) {window.handleError(error)} 
    finally {
        console.log("COMPLETED")
        return Promise.resolve(dataFromPython)
    }
}