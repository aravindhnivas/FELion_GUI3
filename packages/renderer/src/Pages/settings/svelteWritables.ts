import { writable, get, derived } from 'svelte/store'

const setDefault = (key: string) => {
    const initialValue = <string>window.db.get(key)
    const store = window.persistentDB(key, initialValue)
    if(window.isPackaged) {store.set(initialValue)};
    return store
}

export const pythonpath = setDefault("pythonpath")
export const pythonscript = setDefault("pythonscript")
export const felionpy = setDefault("felionpy")

export const developerMode = window.persistentDB("developerMode", import.meta.env.DEV)
if(window.isPackaged) {developerMode.set(false)};

export const pyProgram = derived(
    [developerMode, pythonpath, felionpy],

    ([$developerMode, $pythonpath, $felionpy]) => {
        return $developerMode ? $pythonpath : $felionpy
    }
)

export const pyServerReady = writable(false)
export const pyVersion = window.persistentDB("pyVersion", "")
export const pyServerPORT = window.persistentDB("pyServerPORT", 5050)
export const mainpyfile = derived([developerMode, pythonscript], ([$developerMode, $pythonscript]) => {
    return $developerMode ? window.path.join($pythonscript, 'main.py') : ''
});

export const currentTab = window.persistentDB('settingsActiveTab', 'Configuration')
export const serverDebug = window.persistentDB('serverDebug', false)
export { get };
