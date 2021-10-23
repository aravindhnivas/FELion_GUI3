// Preload (Isolated World)
const { contextBridge, ipcRenderer } = require('electron')
const path = require("path")
const fs = require("fs")
require('source-map-support').install({
    environment: 'browser',
    retrieveSourceMap: function() {

        return {
            url: path.resolve(__dirname, "static/bundle.js"),
            map: fs.readFileSync(path.resolve(__dirname, "static/bundle.js.map"), 'utf8')
        };

    }
});
window.addEventListener('contextmenu', (e) => {
    e.preventDefault()
    const rightClickPosition = {x: e.x, y: e.y}
    ipcRenderer.invoke("contextmenu", rightClickPosition)

}, false);
contextBridge.exposeInMainWorld("appInfo", ipcRenderer.sendSync("appInfo", null))
contextBridge.exposeInMainWorld("__dirname", path.resolve(__dirname, "static/"))
ipcRenderer.on('update-log', (event, info) => console.info(info))
ipcRenderer.on('update-progress', (event, progressObj) => {
    const progressContainer = document.getElementById("update-progress-container")
    progressContainer.style.display = "grid"
    const progressDiv = document.getElementById("update-progress")
    progressDiv.value = progressObj.percent
    console.info(progressObj)
})
ipcRenderer.on('update-log-error', (event, error) => console.error(error))
contextBridge.exposeInMainWorld("checkupdate", () => ipcRenderer.invoke("checkupdate", null))

require("./main/preload-modules")