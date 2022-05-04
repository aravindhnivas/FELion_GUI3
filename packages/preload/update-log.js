import { contextBridge, ipcRenderer } from 'electron'

ipcRenderer.on('update-log', (_, info) => console.warn(info))
ipcRenderer.on('update-progress', (_, progressObj) => {
    const progressContainer = document.getElementById(
        'update-progress-container'
    )

    progressContainer.style.display = 'grid'

    const progressDiv = document.getElementById('update-progress')

    if (progressObj.total > 0) {
        // if total is 0, it means that the update is not yet started
        progressDiv.value = progressObj.percent // update the progress bar
        console.info(progressObj) // log the progress
    }
})

contextBridge.exposeInMainWorld('checkupdate', () => {
    ipcRenderer.invoke('checkupdate', null) // check for updates
    localStorage.setItem('update-error', '') // (if any error occured, it will be set in local storage)
})
