import { writable, get, derived } from 'svelte/store'
export { get }

const pyPath: string = window.path.join(window.ROOT_DIR, 'python3/python')
const pyScriptPath: string = window.path.join(window.ROOT_DIR, 'resources/python_files')

export const developerMode = window.persistentDB("developerMode", <boolean>window.appInfo.isPackaged)

export const pythonpath = window.persistentDB("pythonpath", pyPath)
export const pythonscript = window.persistentDB("pythonscript", pyScriptPath)

export const felionpy = window.persistentDB("felionpy", window.path.join(window.ROOT_DIR, "resources/felionpy/felionpy"))

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
