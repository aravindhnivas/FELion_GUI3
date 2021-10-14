
import { mainPreModal } from "../../svelteWritable";
// import { extractFull } from 'node-7z-forall';

const isPackaged = !__main_location.includes("node_modules");
const copyFiles = (downloadedFile) => {
    try {

        // const app_location = pathResolve(__main_location, "resources/app")
        // fs.emptyDirSync(app_location)
        fs.copySync(downloadedFile, __main_location)
        console.log('success!')

    } catch (err) { console.error(err) }
}





export default async (zipfile, extractedFolder) => {
    if(!isPackaged) return window.createToast("Application not packaged", "danger")
    extractFull(zipfile, extractedFolder, {})
        .then(() => {
            copyFiles(zipfile)
        })
        .catch( (error) => mainPreModal.error(error.stack || error) )
}