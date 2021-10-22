
const { contextBridge, ipcRenderer } = require('electron')
const path = require("path")
const JSONdb = require(path.resolve(__dirname, "../../static/assets/js/JSONdb"))

const makeJSONdb = (file_location) => {
    const db = new JSONdb(file_location)

    return {
        get(key){return db.get(key)},
        set(key, value){return db.set(key, value)},
        has(key){return db.has(key)},

        delete(key){return db.delete(key)}
    }
}
const db_file_location = path.resolve(__dirname, "../../static/db.json")
contextBridge.exposeInMainWorld("db", makeJSONdb(db_file_location))


contextBridge.exposeInMainWorld("appVersion", ipcRenderer.sendSync('appVersion', null))
contextBridge.exposeInMainWorld("JSONdb", makeJSONdb)