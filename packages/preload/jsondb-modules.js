import { contextBridge } from 'electron'
import Store from 'electron-store'

export const db = new Store({name: "db"});

contextBridge.exposeInMainWorld("db", {

    get(key) { return db.get(key) },
    has(key) { return db.has(key) },
    set(key, value) { return db.set(key, value) },
    delete(key) { return db.delete(key) },
    data: ()=>db.store,
    
    clear: ()=>db.clear(),
    reset: ()=>db.reset(),
    path: db.path,
    onDidChange: (key, callback) => db.onDidChange(key, callback),
    onDidAnyChange: (callback) => db.onDidAnyChange(callback),

})