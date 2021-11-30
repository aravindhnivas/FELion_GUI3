const { contextBridge, ipcRenderer } = require('electron')
const {versions} = require("process")
const path = require("path")
const fs = require("fs-extra")

const env = import.meta.env;


contextBridge.exposeInMainWorld("versions", versions)
const appInfo = ipcRenderer.sendSync("appInfo", null)
contextBridge.exposeInMainWorld("appInfo", appInfo)


window.ROOT_DIR = path.join(__dirname, "../../../")
window.PKG_DIR = path.join(ROOT_DIR, "packages")
window.RENDERER_DIR = path.join(PKG_DIR, "renderer")

contextBridge.exposeInMainWorld("ROOT_DIR", ROOT_DIR)
window.publicDirectory = path.join(RENDERER_DIR, "dist/")
contextBridge.exposeInMainWorld("__dirname", publicDirectory)

console.log({__dirname, ROOT_DIR, PKG_DIR, RENDERER_DIR, MODE: env})

window.addEventListener('contextmenu', (e) => {
    e.preventDefault()
    const rightClickPosition = {x: e.x, y: e.y}
    ipcRenderer.invoke("contextmenu", rightClickPosition)
}, false);

fs.ensureDirSync(path.join(appInfo.userData, "config"))

ipcRenderer.on('update-log', (_, info) => console.info(info))
ipcRenderer.on('update-progress', (_, progressObj) => {
    const progressContainer = document.getElementById("update-progress-container")
    progressContainer.style.display = "grid"
    const progressDiv = document.getElementById("update-progress")
    progressDiv.value = progressObj.percent
    console.info(progressObj)
})

ipcRenderer.on('update-log-error', (_, error) => console.error(error))
contextBridge.exposeInMainWorld("checkupdate", () => ipcRenderer.invoke("checkupdate", null))

require("../fs-modules")
require("../path-modules")
require("../child-process-modules")
require("../dialogs-modules")
require("../jsondb-modules")

