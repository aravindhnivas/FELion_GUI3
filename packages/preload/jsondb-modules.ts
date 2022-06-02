import { ipcRenderer } from 'electron'
import { exposeInMainWorld } from './exposeInMainWorld'
import Store from 'electron-store'

export const db = new Store({ name: 'db' })

db.set('updateError', '')

if (!db.has('delayupdate')) {
    db.set('delayupdate', false)
}

db.set('update-status', '')

ipcRenderer.on('db:update', (_event, { key, value }) => {
    db.set(key, value)
    console.info('db:update', { key, value })
})

export const dbObject = {
    get(key: string) {
        return db.get(key)
    },
    has(key) {
        return db.has(key)
    },
    set(key, value) {
        return db.set(key, value)
    },
    delete(key) {
        return db.delete(key)
    },
    data: () => db.store,
    clear: () => db.clear(),
    reset: () => db.reset(),
    path: db.path,
    onDidChange: (key, callback) => db.onDidChange(key, callback),
    onDidAnyChange: (callback) => db.onDidAnyChange(callback),
}

exposeInMainWorld('db', dbObject)
