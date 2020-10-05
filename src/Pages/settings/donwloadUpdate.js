
import {urlzip, get} from "./svelteWritables";
import { updating } from "../../js/functions";
const https = require('https');
const admZip = require('adm-zip');

export function download(updateFolder) {

    return new Promise((resolve, reject)=>{

        updating.set(true)
        const updatefilename = "update.zip"

        const zipFile = path.resolve(updateFolder, updatefilename)

        const response = https.get(get(urlzip), (res) => {

            console.log(`URL: ${get(urlzip)}`)
            console.log('statusCode:', res.statusCode);
            console.log('headers:', res.headers);
            res.pipe(fs.createWriteStream(zipFile))
            console.log("File downloaded")
        })

        response.on("close", () => {
            console.log("Downloading Completed")
            console.log("Extracting files")

            setTimeout(()=>{

                let zip = new admZip(zipFile);
                zip.extractAllTo(updateFolder, /*overwrite*/true);
                console.log("File Extracted")
                resolve("File extracted")
                window.createToast("Downloading Completed")
            }, 1600)
        
        })
    })
}