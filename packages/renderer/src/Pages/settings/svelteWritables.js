
import { writable, get, derived } from "svelte/store";
export { get };

const pyPath = pathJoin(ROOT_DIR, "python3/python")
const pyScriptPath = pathJoin(ROOT_DIR, "resources/python_files")

if(!db.get("pythonpath")) {db.set("pythonpath", pyPath)}
if(!db.get("pythonscript")) {db.set("pythonscript", pyScriptPath)}

export const pythonpath = writable(db.get("pythonpath"))
export const pythonscript = writable(db.get("pythonscript"))

export const developerMode = writable(db.get("developerMode") ?? appInfo.isPackaged)
console.log("developerMode: ", db.get("developerMode"), get(developerMode))
export const pyProgram = derived([developerMode, pythonpath], ([$developerMode, $pythonpath]) => {
    return $developerMode ? $pythonpath : pathJoin(ROOT_DIR, "resources/felionpy/felionpy")
});

export const pyVersion = writable("")
export const pyServerPORT = writable(db.get("pyServerPORT") || 5050)
export const pyServerReady = writable(false)
export const suppressInitialDeveloperWarning = writable(db.get("suppressInitialDeveloperWarning") || false)
