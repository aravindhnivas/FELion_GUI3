
import { contextBridge, ipcRenderer } from 'electron'
contextBridge.exposeInMainWorld("startServer", () => {
    ipcRenderer.send('startServer')
})
contextBridge.exposeInMainWorld("stopServer", () => {
    ipcRenderer.send('stopServer')
})
