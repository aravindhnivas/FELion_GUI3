import { ipcRenderer } from 'electron'
import { db } from './persistentDB'
import { exposeInMainWorld } from './exposeInMainWorld'
import {isPackaged} from './definedEnv'

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
    console.warn('checking for update')

    if(!isPackaged) return db.set('updateError', 'Cannot check for updates in dev mode')
    if (!navigator.onLine) return db.set('updateError', 'No internet connection')
    
    const updateCheckDiv = document.getElementById('update-check-status')
    if(updateCheckDiv) {
        updateCheckDiv.textContent = new Date().toLocaleString() 
    }

    ipcRenderer.invoke('checkupdate', null)
    localStorage.setItem('update-error', '')
}
// checkupdate()
exposeInMainWorld('checkupdate', checkupdate)
exposeInMainWorld('quitAndInstall', () => {
    ipcRenderer.invoke('quitAndInstall', null)
})
