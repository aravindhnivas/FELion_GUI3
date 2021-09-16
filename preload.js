// Preload (Isolated World)
// require('source-map-support/register')
const { contextBridge } = require('electron')
const { ipcRenderer } = require('electron')
const path = require("path")
const copy = require('recursive-copy');
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
contextBridge.exposeInMainWorld("copy", (src, dest, opts, callback)=>copy(src, dest, opts, callback))