import { ipcRenderer } from 'electron'
import logger from 'electron-log'

logger.info('preload: loading...')

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

logger.info('preload: loaded')
window.addEventListener('DOMContentLoaded', () => {
    logger.info('Preload: DOM fully loaded and parsed')
})
