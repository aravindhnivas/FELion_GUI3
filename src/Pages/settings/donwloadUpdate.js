
import {urlzip, get} from "./svelteWritables";
import { updating } from "../../js/functions";
import https from 'https'
export function download(updateFolder) {

    return new Promise(async (resolve, reject)=>{

        try {
            updating.set(true)
            const updatefilename = "update.zip"
            const zipFile = pathResolve(updateFolder, updatefilename)

            const urlZip = get(urlzip)
            
            await request(urlZip, zipFile)

            
            
            
            const zip = admZip(zipFile)
            zip.extractAllTo(updateFolder, /*overwrite*/true)
            console.log("File Extracted")
            resolve("File extracted")
            window.createToast("Downloading Completed")
        } catch (error) {reject(error)}
    })
}