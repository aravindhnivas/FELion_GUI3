
import {pyServerPORT, get } from "../settings/svelteWritables";
export default async function({target=null, general=false, pyfile, args}) {
    
    try {
        
        if(!general) target?.classList.add("is-loading")

        const outputFile = pathJoin(appInfo.temp, "FELion_GUI3", pyfile.split(".").at(-1) + "_data.json")
        if(fs.existsSync(outputFile)) fs.removeSync(outputFile)
    
        const URL = `http://localhost:${get(pyServerPORT)}/felionpy/compute`
    
        const method =  'POST'
        const headers =  {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        const body =  JSON.stringify({pyfile, args})
        const response = await fetch(URL, {method, headers, body})

        if(target?.classList.contains("is-loading")) {
            target.classList.remove("is-loading")
        }

        if(!response.ok) return Promise.reject(`Response status: ${response.statusText}`)

        const {timeConsumed} = await response.json()
        console.warn(timeConsumed)

        if(general) { return Promise.resolve() }

        if(!fs.existsSync(outputFile)) {
            console.warn(`${outputFile} file doesn't exists`)
            window.handleError(`${outputFile} file doesn't exists`)
        }

        
        const dataFromPython = fs.readJsonSync(outputFile)
        return Promise.resolve(dataFromPython)
    
    } catch (error) { 
        if(target?.classList.contains("is-loading")) {
            target.classList.remove("is-loading")
        }
        return Promise.reject(error)
    }
    
}