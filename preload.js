// Preload (Isolated World)
// require('source-map-support/register')
// require('dotenv').config(__dirname)
const { contextBridge, ipcRenderer} = require('electron')
const path = require("path")
const copy = require('recursive-copy');
const os = require('os');
const fs = require("fs-extra")
window.addEventListener('contextmenu', (e) => {

    e.preventDefault()
    const rightClickPosition = {x: e.x, y: e.y}
    ipcRenderer.invoke("contextmenu", rightClickPosition)
}, false)

window.addEventListener('DOMContentLoaded', ()=>{
    console.log(__dirname, "loaded")
})
require("./main/preload-modules")


// const env_variables = JSON.stringify(process.env)
// contextBridge.exposeInMainWorld("__env", JSON.parse(env_variables))

contextBridge.exposeInMainWorld("__dirname", path.resolve(__dirname, "static/"))
contextBridge.exposeInMainWorld("__main_location", path.dirname(process.execPath))

const temp = path.resolve(os.tmpdir(), "FELion")
fs.ensureDirSync(temp)
contextBridge.exposeInMainWorld("TEMP", temp)

contextBridge.exposeInMainWorld("copy", (src, dest, opts, callback)=>copy(src, dest, opts, callback))
