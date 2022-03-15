import { ipcRenderer } from 'electron'

window.addEventListener('contextmenu', (e) => {
    e.preventDefault()
    const rightClickPosition = { x: e.x, y: e.y }
    ipcRenderer.invoke("contextmenu", rightClickPosition)
}, false);

import "./definedENV"
import "./update-log"
import "./mangeServer"
import "./fs-modules"

import "./path-modules"
import "./child-process-modules"
import "./dialogs-modules"
import "./jsondb-modules"
import "./utils/logger"