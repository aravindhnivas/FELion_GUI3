import Store from 'electron-store'
import path from 'path'

export const db = new Store({ name: 'db' })
// Store.initRenderer()

export const ROOT_DIR = path.join(__dirname, '../../../')
export const PKG_DIR = path.join(ROOT_DIR, 'packages')
export const RENDERER_DIR = path.join(PKG_DIR, 'renderer')
if (!db.has('pythonpath')) {
    db.set('pythonpath', path.join(ROOT_DIR, 'python3/python'))
}

if (!db.has('pythonscript')) {
    db.set('pythonscript', path.join(ROOT_DIR, 'resources/python_files'))
}

db.set('pyVersion', '')
