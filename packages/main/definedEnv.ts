import { app, ipcMain } from 'electron'
import Store from 'electron-store'
import * as path from 'path'

const dbName = `db${import.meta.env.DEV ? '-dev': ''}`
export const db = new Store({ name: dbName })

ipcMain.on('dbName',  (event, _arg) => {
    event.returnValue = dbName
})

export const ROOT_DIR = app.isPackaged ? path.dirname(app.getPath("module")) : app.getAppPath()

if (!db.has('pythonpath')) {
    db.set('pythonpath', path.join(ROOT_DIR, 'python3/python'))
}
if (app.isPackaged || !db.has('pythonscript')) {
    db.set('pythonscript', path.join(ROOT_DIR, 'resources/python_files'))
}
if (app.isPackaged || !db.has('felionpy')) {
    db.set('felionpy', path.join(ROOT_DIR, 'resources/felionpy/felionpy'))
}

if (app.isPackaged || !db.has('developerMode')) {
    db.set('developerMode', false)
}

db.set('pyVersion', '')