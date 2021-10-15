
import { mainPreModal } from "../../svelteWritable";
const copyFiles = () => {
    try {
        // const app_location = pathResolve(__main_location, "resources/app")
        // fs.emptyDirSync(app_location)
        fs.copySync(zipfolder, __main_location)

        console.log('success!')
    } catch (err) { console.error(err) }
}
const handleError = (error) => mainPreModal.error(error.stack || error)

export default async () => {
    extractFull(zipFile, zipfolder, {}).then(copyFiles).catch(handleError)
}