
import {urlzip, get} from "./svelteWritables";
import { updating } from "../../js/functions";

function downloadFromGit(urlZip, zipFile) {

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
export function download(updateFolder) {

    return new Promise(async (resolve, reject)=>{

        try {
            updating.set(true)
            const updatefilename = "update.zip"
            const zipFile = pathResolve(updateFolder, updatefilename)

            const urlZip = get(urlzip)
            const response = await downloadFromGit(urlZip, zipFile)
            console.log(response)
            const zip = admZip(zipFile)
            zip.extractAllTo(updateFolder, /*overwrite*/true)
            console.log("File Extracted")
            resolve("File extracted")
            window.createToast("Downloading Completed")
        } catch (error) {reject(error)}
    })
}