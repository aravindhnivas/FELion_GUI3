import { contextBridge, ipcRenderer } from 'electron'
import { versions } from "process"
import path from "path"
import fs from "fs-extra"

const env = import.meta.env;
contextBridge.exposeInMainWorld("env", env)

contextBridge.exposeInMainWorld("versions", versions)
const appInfo = ipcRenderer.sendSync("appInfo", null)
contextBridge.exposeInMainWorld("appInfo", appInfo)
const { isPackaged } = appInfo

const ROOT_DIR = isPackaged ? path.dirname(appInfo.module) : path.join(__dirname, "../../../")
const PKG_DIR = path.join(ROOT_DIR, "packages")
const RENDERER_DIR = path.join(PKG_DIR, "renderer")

contextBridge.exposeInMainWorld("ROOT_DIR", ROOT_DIR)
const publicDirectory = path.join(RENDERER_DIR, isPackaged ? "dist" : "public")
contextBridge.exposeInMainWorld("__dirname", publicDirectory)
console.table({ ROOT_DIR, PKG_DIR, RENDERER_DIR, publicDirectory })
console.table(env)

window.addEventListener('contextmenu', (e) => {
    e.preventDefault()
    const rightClickPosition = { x: e.x, y: e.y }
    ipcRenderer.invoke("contextmenu", rightClickPosition)
}, false);

fs.ensureDirSync(path.join(appInfo.userData, "config"))

ipcRenderer.on('update-log', (_, info) => console.warning(JSON.stringify(info)))
ipcRenderer.on('update-progress', (_, progressObj) => {
    const progressContainer = document.getElementById("update-progress-container")
    progressContainer.style.display = "grid"
    const progressDiv = document.getElementById("update-progress")
    progressDiv.value = progressObj.percent
    console.info(progressObj)
})

ipcRenderer.on('update-log-error', (_, error) => console.error(error))
contextBridge.exposeInMainWorld("checkupdate", () => ipcRenderer.invoke("checkupdate", null))

import "./fs-modules"
import "./path-modules"
import "./child-process-modules"
import "./dialogs-modules"
import "./jsondb-modules"