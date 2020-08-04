
import {backupName, get} from "./svelteWritables";
import {browse} from "../../components/Layout.svelte";
const copy = require('recursive-copy');

// const copyfile = async ({dest, src}={}) => {


//     try {
//         const folderfiles = fs.readdirSync(src)
//         console.log({dest, src})
//         if(!fs.existsSync(dest)) fs.mkdirSync(dest)

//         const files = folderfiles.filter(f=>fs.statSync(f).isFile() && !f.startsWith("."))

//         const folders = folderfiles.filter(f=>fs.statSync(f).isDirectory() && !f.startsWith(".") && f !== "node_modules" && f !== "dist" && f !== "python3")

//         console.log("Files: ", files, "Folders: ", folders)

//         await asyncForEach(files, (file)=>{
//             console.log("Copying file: ", file, " in folder ", dest)
//             fs.copyFileSync(path.join(src, file), path.join(dest, file) )
//         })
//         await asyncForEach(folders, (folder)=>copyfile({src:path.join(src, folder), dest:path.join(dest, folder) }))

//         return Promise.resolve("Folder transfer completed")
//     } catch (error) {
//         return Promise.reject(error)        
//     }
// }

export function transferFiles({dest, src, includeNode=true}={}) {
    return new Promise((resolve, reject)=>{


        const options = {overwrite: true, filter: includeNode ?  [] : fs.readdirSync(src).filter(file => file != "node_modules")}
        
        copy(src, dest, options)
        
            .on(copy.events.COPY_FILE_START, function(copyOperation) {
                console.info('Copying file ' + copyOperation.src + '...');
            })
            
            
            .on(copy.events.COPY_FILE_COMPLETE, function(copyOperation) {
            
                console.info('Copied to ' + copyOperation.dest);
            })
            
            .on(copy.events.ERROR, function(error, copyOperation) {
                console.error('Unable to copy ' + copyOperation.dest);
            })
            
            .then(function(results) {
                resolve(results)
                console.info(results.length + ' file(s) copied');
            })
            
            .catch(function(error) {
                reject(error)
            
                return console.error('Copy failed: ' + error);
        });

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

                await transferFiles({dest, src, includeNode:false})
                resolve()
            })

            .catch(err=>{

                console.log(err)
                reject(err)

            })

            .finally(()=>target.classList.toggle("is-loading"))

    })

}