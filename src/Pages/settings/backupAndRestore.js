
import {backupName, get} from "./svelteWritables";
import {browse} from "$components/Layout.svelte";
// const copy = require('recursive-copy');
// import copy from "recursive-copy";
export function transferFiles({dest, src, includeNode=true}={}) {
    return new Promise((resolve, reject)=>{


        // const filter = readdirSync(src).filter((file) => {return file !== "node_modules" && file !== "python3"})

        // const options = {overwrite: true, filter: includeNode ?  readdirSync(src) : filter}
        
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
                if (result) { folderName = result[0] } else {return console.log("Cancelled")}
                
        
                console.log("Selected folder: ", folderName)
        
                let dest, src;
                if(method === "backup") {

                    dest = pathResolve(folderName, get(backupName))
                    src = pathResolve(__dirname, "..")
                } else {

                    dest = pathResolve(__dirname, "..")
                    src = pathResolve(folderName)
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