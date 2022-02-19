import { contextBridge, ipcRenderer } from 'electron'
import Store from 'electron-store'

contextBridge.exposeInMainWorld("appVersion", ipcRenderer.sendSync('appVersion', null))
const store = new Store({name: "db"});
// const data = store.store
// console.log(data)

contextBridge.exposeInMainWorld("db", {
    get(key) { return store.get(key) },
    set(key, value) { return store.set(key, value) },
    delete(key) { return store.delete(key) },

    data: ()=>store.store,
    clear: ()=>store.clear(),
    reset: ()=>store.reset(),
    path: store.path,
    onDidChange: (key, callback) => store.onDidChange(key, callback),
    onDidAnyChange: (callback) => store.onDidAnyChange(callback),
})

