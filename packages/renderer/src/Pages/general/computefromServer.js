
import {pyServerPORT, get } from "../settings/svelteWritables";
export default async function({target=null, general=false, pyfile, args}) {
    
    try {
        
        if(!general) target?.classList.add("is-loading")

        const outputFile = pathJoin(appInfo.temp, "FELion_GUI3", pyfile.split(".").at(-1) + "_data.json")
        if(fs.existsSync(outputFile)) fs.removeSync(outputFile)
    
        const URL = `http://localhost:${get(pyServerPORT)}/`
    
        const method = 'POST'
        const headers = {
            'Content-type': 'application/json',
            // 'Accept': 'application/json'
        }

        const body =  JSON.stringify({pyfile, args})
        const response = await fetch(URL, {method, headers, body})

        if(target?.classList.contains("is-loading")) {
            target.classList.remove("is-loading")
        }

        console.warn(response)
        if(!response.ok) {
            const jsonErrorInfo = await response.json()
            return Promise.reject(jsonErrorInfo?.error || jsonErrorInfo)
        }

        const {timeConsumed} = await response.json()
        console.warn({timeConsumed})

        if(general) { return Promise.resolve() }

        if(!fs.existsSync(outputFile)) {
            return Promise.reject(`${outputFile} file doesn't exists`)
        }
        
        const dataFromPython = fs.readJsonSync(outputFile)
        if(!dataFromPython) {
            return Promise.reject("received invalid output data from python. check the output json file")
        }

        return Promise.resolve(dataFromPython)
    
    } catch (error) { 
        if(target?.classList.contains("is-loading")) {
            target.classList.remove("is-loading")
        }
        const msg = error.message
        const details = error.stack || error
        console.error(error)
        return Promise.reject(
            `Error after receiving data from python \n${msg} \n${details}`
        )
    }
    
}