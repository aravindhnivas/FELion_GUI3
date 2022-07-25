import { app, ipcMain } from 'electron'
import Store from 'electron-store'
import * as path from 'path'

const dbName = `db${import.meta.env.DEV ? '-dev': ''}`
export const db = new Store({ name: dbName })

ipcMain.on('dbName',  (event, _arg) => {
    event.returnValue = dbName
})

export const ROOT_DIR = app.isPackaged ? path.dirname(app.getPath("module")) : app.getAppPath()
export const PKG_DIR = path.join(ROOT_DIR, 'packages')
export const RENDERER_DIR = path.join(PKG_DIR, 'renderer')
console.table({ __dirname, ROOT_DIR, PKG_DIR, RENDERER_DIR, app: app.getAppPath() })
if (!db.has('pythonpath')) {
    db.set('pythonpath', path.join(ROOT_DIR, 'python3/python'))
}

if (!db.has('pythonscript')) {
    db.set('pythonscript', path.join(ROOT_DIR, 'resources/python_files'))
}

if (!db.has('felionpy')) {
    db.set('felionpy', path.join(ROOT_DIR, 'resources/felionpy/felionpy'))
}

db.set('pyVersion', '')
