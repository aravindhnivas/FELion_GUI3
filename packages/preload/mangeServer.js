import { contextBridge, ipcRenderer } from 'electron'
contextBridge.exposeInMainWorld('startServer', async () => {
    console.warn('starting server')
    return ipcRenderer.invoke('startServer')
})
contextBridge.exposeInMainWorld('stopServer', () => {
    console.warn('invoking stopServer')
    ipcRenderer.send('stopServer')
})
