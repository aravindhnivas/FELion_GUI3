
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld("dialogs", {
    showMessageBoxSync: async (args) => await ipcRenderer.invoke("showMessageBoxSync", args),
    showOpenDialogSync: async (args) => {
        console.log(args)

        const result = await ipcRenderer.invoke("showOpenDialogSync", args)
        console.log(result)
        return result
    }

})
contextBridge.exposeInMainWorld("reload", ()=>ipcRenderer.invoke('reload'))
contextBridge.exposeInMainWorld("relaunch", ()=>ipcRenderer.invoke('relaunch'))