
import {filedetails} from "./svelteWritables";

export function get_details_func({dataFromPython}={}) {
    
    const info = dataFromPython.files.map(data=>{
        let {filename, trap, res, b0, range} = data
        let [min, max] = range
        return {filename, min, max, trap, b0, res, precursor:"", ie:"", temp:"", id:getID()}

    })
    filedetails.set(info)
    
}