
import { contextBridge, ipcRenderer } from 'electron'
ipcRenderer.on('update-log', (_, info) => console.warn(info))
ipcRenderer.on('update-progress', (_, progressObj) => {
    const progressContainer = document.getElementById("update-progress-container")
    progressContainer.style.display = "grid"
    const progressDiv = document.getElementById("update-progress")
    progressDiv.value = progressObj.percent
    console.info(progressObj)
})
// localStorage.setItem("update-error", "")
// ipcRenderer.on('update-log-error', (_, error) => {console.error(error); localStorage.setItem("update-error", error)})

contextBridge.exposeInMainWorld("checkupdate", () => {
    ipcRenderer.invoke("checkupdate", null);
    localStorage.setItem("update-error", "")

})