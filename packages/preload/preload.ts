import { ipcRenderer } from 'electron'

console.info('preload: loading...')
window.addEventListener(
    'contextmenu',
    (e) => {
        e.preventDefault()
        const rightClickPosition = { x: e.x, y: e.y }
        ipcRenderer.send('contextmenu', rightClickPosition)
    },
    false
)

import './definedEnv'
import './update-log'
import './mangeServer'
import './fs-modules'
import './path-modules'
import './child-process-modules'
import './dialogs-modules'
import './jsondb-modules'
import './utils/logger'

console.info('preload: loaded')
window.addEventListener('DOMContentLoaded', () => {
    const appVersion: string = ipcRenderer.sendSync('appVersion', null)
    const title = document.getElementById('app-title')
    if (title) {
        title.textContent = `FELion_GUI v${appVersion}`
    }
    console.info('Preload: DOM fully loaded and parsed')
})
