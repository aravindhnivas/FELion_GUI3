// Preload (Isolated World)
// require('source-map-support/register')
const { contextBridge, ipcRenderer } = require('electron')
const path = require("path")
const os = require('os');
const fs = require("fs-extra");


window.addEventListener('contextmenu', (e) => {
    e.preventDefault()
    const rightClickPosition = {x: e.x, y: e.y}
    ipcRenderer.invoke("contextmenu", rightClickPosition)

}, false)

window.addEventListener('DOMContentLoaded', ()=>{
    console.log(__dirname, "loaded")
})
require("./main/preload-modules")



contextBridge.exposeInMainWorld("__dirname", path.resolve(__dirname, "static/"))
contextBridge.exposeInMainWorld("__main_location", path.dirname(process.execPath))

const temp = path.resolve(os.tmpdir(), "FELion")
fs.ensureDirSync(temp)

contextBridge.exposeInMainWorld("TEMP", temp)
contextBridge.exposeInMainWorld("updateFELion", (args=null) => ipcRenderer.invoke("update", args) )
console.log(process.argv)