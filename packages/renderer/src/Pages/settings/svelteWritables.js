import { writable, get, derived } from 'svelte/store'
export { get }

const pyPath = window.path.join(window.ROOT_DIR, 'python3/python')
const pyScriptPath = window.path.join(window.ROOT_DIR, 'resources/python_files')

if (!window.db.get('pythonpath')) {
    window.db.set('pythonpath', pyPath)
}
if (!window.db.get('pythonscript')) {
    window.db.set('pythonscript', pyScriptPath)
}

export const pythonpath = writable(window.db.get('pythonpath'))
export const pythonscript = writable(window.db.get('pythonscript'))

export const developerMode = writable(window.db.get('developerMode') ?? window.appInfo.isPackaged)
console.log('developerMode: ', window.db.get('developerMode'), get(developerMode))
export const pyProgram = derived([developerMode, pythonpath], ([$developerMode, $pythonpath]) => {
    return $developerMode ? $pythonpath : window.path.join(window.ROOT_DIR, 'resources/felionpy/felionpy')
    // return $developerMode ? $pythonpath : window.path.join(window.ROOT_DIR, "resources/python_files/nuitka/main.dist/main")
})
export const mainpyfile = derived([developerMode, pythonscript], ([$developerMode, $pythonscript]) => {
    return $developerMode ? window.path.join($pythonscript, 'main.py') : ''
})

export const pyVersion = writable(window.db.get('pyVersion') || '')
export const pyServerPORT = writable(window.db.get('pyServerPORT') || 5050)
window.db.onDidChange('pyServerPORT', (value) => pyServerPORT.set(value))

export const pyServerReady = writable(false)
export const suppressInitialDeveloperWarning = writable(window.db.get('suppressInitialDeveloperWarning') || false)
