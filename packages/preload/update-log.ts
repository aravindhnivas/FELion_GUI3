import { ipcRenderer } from 'electron'
import { exposeInMainWorld } from './exposeInMainWorld'
ipcRenderer.on('update-log', (_, info) => console.warn(info))
ipcRenderer.on('update-progress', (_, progressObj) => {
    const progressContainer = <HTMLElement>document.getElementById('update-progress-container')
    progressContainer.style.display = 'grid'
    const progressDiv = <HTMLProgressElement>document.getElementById('update-progress')
    if (progressObj.total > 0) {
        progressDiv.value = progressObj.percent
        console.info(progressObj)
    }
})

export function checkupdate(): void {
    ipcRenderer.invoke('checkupdate', null)
    localStorage.setItem('update-error', '')
}

exposeInMainWorld('checkupdate', checkupdate)
