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

import './definedENV'
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
    console.info('Preload: DOM fully loaded and parsed')
})
