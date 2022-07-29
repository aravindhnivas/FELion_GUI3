import { app, ipcMain } from 'electron'
import Store from 'electron-store'
import * as path from 'path'
// import { platform } from 'process'

const dbName = `db${import.meta.env.DEV ? '-dev': ''}`

export const db = new Store({ name: dbName })

ipcMain.on('dbName',  (event, _arg) => {
    event.returnValue = dbName
})

export const ROOT_DIR = app.isPackaged ? path.dirname(app.getPath("module")) : app.getAppPath()
export const resource_directory = app.isPackaged ? path.dirname(app.getAppPath()) : path.join(ROOT_DIR, 'resources')

if (!db.has('pythonpath')) {
    db.set('pythonpath', path.join(ROOT_DIR, 'python3/python'))
}
if (import.meta.env.PROD|| !db.has('pythonscript')) {
    console.log('setting default values for pythonscript')
    db.set('pythonscript', path.join(resource_directory, 'python_files'))
}
if (import.meta.env.PROD|| !db.has('felionpy')) {
    console.log('setting default values for felionpy')
    db.set('felionpy', path.join(resource_directory, 'felionpy/felionpy'))
}

if (import.meta.env.PROD|| !db.has('developerMode')) {
    console.log('setting default values for developerMode')
    db.set('developerMode', false)
}

db.set('pyVersion', '')
