// Preload (Isolated World)
const { contextBridge, ipcRenderer, app } = require('electron')
const path = require("path")
window.addEventListener('contextmenu', (e) => {
    e.preventDefault()
    const rightClickPosition = {x: e.x, y: e.y}
    ipcRenderer.invoke("contextmenu", rightClickPosition)

}, false)
window.addEventListener('DOMContentLoaded', ()=>{console.log(__dirname, "loaded")})
require("./main/preload-modules")
contextBridge.exposeInMainWorld("__dirname", path.resolve(__dirname, "static/"))