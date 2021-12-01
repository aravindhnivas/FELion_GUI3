
const { contextBridge, ipcRenderer } = require('electron')
const path = require("path")

const publicDirectory = path.join(
    __dirname, "../renderer", 
    isPackaged ? "dist" : "public"

)

const JSONdb = require(path.join(publicDirectory, "assets/js/JSONdb" ))


const makeJSONdb = (file_location) => {
    const db = new JSONdb(file_location)
    return {
        get(key){return db.get(key)},
        set(key, value){return db.set(key, value)},
        has(key){return db.has(key)},
        delete(key){return db.delete(key)},
        JSON: () => db.JSON()
    }
}
contextBridge.exposeInMainWorld("appVersion", ipcRenderer.sendSync('appVersion', null))
contextBridge.exposeInMainWorld("JSONdb", makeJSONdb)
