import { ipcRenderer } from 'electron'
import { exposeInMainWorld } from './exposeInMainWorld'

export const startServer = async () => {
    console.warn('starting server')
    return ipcRenderer.invoke('startServer')
}

export const stopServer = () => {
    console.warn('invoking stopServer')
    ipcRenderer.send('stopServer')
}

exposeInMainWorld('startServer', startServer)
exposeInMainWorld('stopServer', stopServer)
