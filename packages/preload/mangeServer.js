
import { contextBridge, ipcRenderer } from 'electron'
contextBridge.exposeInMainWorld("restartServer", () => {
    ipcRenderer.send('restartServer')
})
