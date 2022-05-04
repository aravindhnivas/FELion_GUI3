import { contextBridge, ipcRenderer } from 'electron'

ipcRenderer.on('update-log', (_, info) => console.warn(info))
ipcRenderer.on('update-progress', (_, progressObj) => {
    const progressContainer = document.getElementById(
        'update-progress-container'
    )
    progressContainer.style.display = 'grid'
    const progressDiv = document.getElementById('update-progress')
    progressDiv.value = progressObj.percent
    
    console.info(progressObj)
    
    if(progressObj.percent === 100) {
        const updateCheckBtn = document.getElementById('updateCheckBtn')
        if(updateCheckBtn?.classList.contains('is-loading')) {
            updateCheckBtn.classList.toggle('is-loading')
        }
        
    }

})

contextBridge.exposeInMainWorld('checkupdate', () => {
    ipcRenderer.invoke('checkupdate', null)
    localStorage.setItem('update-error', '')
})
