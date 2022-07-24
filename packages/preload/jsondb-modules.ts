import { ipcRenderer } from 'electron'
import { exposeInMainWorld } from './exposeInMainWorld'
import {db, persistentDB} from './persistentDB'
// import Store from 'electron-store'
// export const db = new Store({ name: 'db' })
// export const db = new Store({ name: 'db' })

db.set('updateError', '')

if (!db.has('delayupdate')) {
    db.set('delayupdate', false)
}

db.set('update-status', '')

ipcRenderer.on('db:update', (_event, { key, value }) => {
    db.set(key, value)
    console.info('db:update', { key, value })
})

// type ValueType = string | number | boolean

export const dbObject = {
    get(key: string)  {
        const output = db.get(key) ?? ''
        return output
    },
    has(key: string) {
        return db.has(key)
    },
    set(key: string, value) {
        return db.set(key, value)
    },
    delete(key: string) {
        return db.delete(key)
    },
    store: () => {return db.store || {}},
    clear: () => db.clear(),
    reset: () => db.reset(),
    path: db.path,
    onDidChange: <T>(key: string, callback: (value: T) => unknown ) => db.onDidChange(key, callback),
    onDidAnyChange: (callback: (value: Object) => unknown ) => db.onDidAnyChange(callback),
}

exposeInMainWorld('db', dbObject)
exposeInMainWorld('persistentDB', <T>(key: string, value: T) => persistentDB(key, value))
