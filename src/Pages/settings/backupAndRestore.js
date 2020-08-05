
import {backupName, get} from "./svelteWritables";
import {browse} from "../../components/Layout.svelte";
const copy = require('recursive-copy');

export function transferFiles({dest, src, includeNode=true}={}) {
    return new Promise((resolve, reject)=>{


        // const filter = fs.readdirSync(src).filter((file) => {return file !== "node_modules" && file !== "python3"})

        // const options = {overwrite: true, filter: includeNode ?  fs.readdirSync(src) : filter}
        
        // console.log(options)

        copy(src, dest, {overwrite: true}, function(error, results) {
        
            if (error) {
        
                console.error('Copy failed: ' + error);
                window.createToast("Update failed.\nMaybe the user doesn't have necessary persmission to write files in the disk", "danger")

                reject(error)
            } else {
                console.info('Copied ' + results.length + ' files')

                window.createToast("Transfer completed.", "success")
                resolve(results)
            }
        })
    })
}

export function backupRestore({event, method="backup"}={}) {

    return new Promise((resolve, reject)=> {
        
        let target = event.target

        target.classList.toggle("is-loading")

        browse({dir:true})

            .then( async (result) =>{
                let folderName;
                if (!result.canceled) { folderName = result.filePaths[0] } else {return console.log("Cancelled")}
                
        
                console.log("Selected folder: ", folderName)
        
                let dest, src;
                if(method === "backup") {

                    dest = path.resolve(folderName, get(backupName))
                    src = path.resolve(__dirname, "..")
                } else {

                    dest = path.resolve(__dirname, "..")
                    src = path.resolve(folderName)
                }
                console.info(`Destination: ${dest}\nSource: ${src}\n`)

                await transferFiles({dest, src, includeNode:false})
                resolve()
            })

            .catch(err=>{

                console.log(err)
                reject(err.stack)

            })

            .finally(()=>target.classList.toggle("is-loading"))

    })

}