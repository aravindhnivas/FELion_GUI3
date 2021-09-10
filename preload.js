// Preload (Isolated World)
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('myAPI', {
    desktop: true
})

window.addEventListener('contextmenu', (e) => {
    e.preventDefault()
    const {x, y} = e
    ipcRenderer.invoke('contextmenu', {x, y})
}, false)