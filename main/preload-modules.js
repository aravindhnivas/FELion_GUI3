
const { contextBridge, process } = require('electron')
const {versions} = require("process")
require("./preload/fs-modules")
require("./preload/path-modules")
require("./preload/child-process-modules")
require("./preload/dialogs-modules")
require("./preload/jsondb-modules")

const admZip = require("adm-zip")
contextBridge.exposeInMainWorld("admZip", (zipFile)=>{
    const zip = new admZip(zipFile);

    return {
        extractAllTo(updateFolder, overwrite){zip.extractAllTo(updateFolder, overwrite)}
    }
})



contextBridge.exposeInMainWorld("versions", versions)