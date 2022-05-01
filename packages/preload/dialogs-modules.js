import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('dialogs', {
    showOpenDialogSync: (args) =>
        ipcRenderer.sendSync('showOpenDialogSync', args),
    showMessageBox: async (args) => ipcRenderer.invoke('showMessageBox', args),
})
contextBridge.exposeInMainWorld('reload', () => ipcRenderer.invoke('reload'))
contextBridge.exposeInMainWorld('relaunch', () =>
    ipcRenderer.invoke('relaunch')
)
