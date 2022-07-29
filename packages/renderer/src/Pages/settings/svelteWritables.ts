import { writable, get, derived } from 'svelte/store'

export const developerMode = window.persistentDB("developerMode", <boolean>window.isPackaged)
export const pythonpath = window.persistentDB("pythonpath", <string>window.db.get("pythonpath"))
export const pythonscript = window.persistentDB("pythonscript", <string>window.db.get("pythonscript"))
export const felionpy = window.persistentDB("felionpy", <string>window.db.get("felionpy"))
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
})

export { get }
