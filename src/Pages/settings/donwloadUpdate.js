
// import {urlzip, get} from "./svelteWritables";
import { updating } from "../../js/functions";
import update from "./update.js";

const filename = "update.7z"
const foldername = "update"
const {urlZip} = versionFileJSON

const zipFile = pathResolve(TEMP, filename)
const extractedFolder = pathResolve(TEMP, foldername)
function downloadFromGit() {

    return new Promise((resolve, reject)=>{

        const writer = fs.createWriteStream(zipFile)

        writer.on("finish", () => resolve("Download completed") )


        fetch(urlZip)
            .then(response => response.body)
            .then(body => {
                const reader = body.getReader();
                reader.read()
                    .then( async function processFile({ done, value }) {
                        if (done) {
                            console.log("Stream complete");
                            writer.end()
                            return;
                        }
                        writer.write(value)
                        return reader.read().then(processFile);
                    })
            })
            .catch(err => reject(err))
    })
}


export function download() {
    return new Promise(async (resolve, reject)=>{
        try {

            updating.set(true)
            const response = await downloadFromGit(urlZip, zipFile)
            console.log(response)
            update(zipFile, extractedFolder)

            fs.emptyDirSync(TEMP)
        } catch (error) {reject(error)}
    })

}