
import { contextBridge, ipcRenderer } from 'electron'
contextBridge.exposeInMainWorld("startServer", async () => {
    return ipcRenderer.invoke('startServer')
})
contextBridge.exposeInMainWorld("stopServer", () => {
    ipcRenderer.send('stopServer')
})
