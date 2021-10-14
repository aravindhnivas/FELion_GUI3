
const { contextBridge } = require('electron')
const path = require("path")
const fs = require("fs-extra")

const JSONdb = require(path.resolve(__dirname, "../../static/assets/js/JSONdb"))
const db = new JSONdb(path.resolve(__dirname, "../../static/db.json"))

contextBridge.exposeInMainWorld("db", {
    get(key){return db.get(key)},
    set(key, value){return db.set(key, value)},
    has(key){return db.has(key)},

    delete(key){return db.delete(key)}
})
const versionFile_ = path.resolve(__dirname, "../../version.json")




// const versionFileContent = fs.readFileSync(versionFile_).toString("utf-8")
// const versionFileJSON = JSON.parse(versionFileContent)
const versionFileJSON = fs.readJSONSync(versionFile_)
const currentVersion = versionFileJSON.version
db.set("version", currentVersion)
contextBridge.exposeInMainWorld("versionFile_", versionFile_)

// contextBridge.exposeInMainWorld("versionFileContent", versionFileContent)
contextBridge.exposeInMainWorld("versionFileJSON", versionFileJSON)
contextBridge.exposeInMainWorld("currentVersion", currentVersion)

contextBridge.exposeInMainWorld("JSONdb", (config)=> {
    const db = new JSONdb(config)
    return {
        get(key){return db.get(key)},
        set(key, value){return db.set(key, value)},
        has(key){return db.has(key)},
        delete(key){return db.delete(key)}
    }

})