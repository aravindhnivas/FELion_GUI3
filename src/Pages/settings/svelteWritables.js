
import { writable, get } from "svelte/store";
export { get };

if (!db.get("pythonpath")) db.set("pythonpath", pathResolve(__dirname, "../python3/python"))
if (!db.get("pythonscript")) db.set("pythonscript", pathResolve(__dirname, "assets/python_files"))
export const pythonpath = writable(db.get("pythonpath"))

export const pythonscript = writable(db.get("pythonscript"))
export const pyVersion = writable("")
export const developerMode = writable(db.get("developerMode") || false)
export const suppressInitialDeveloperWarning = writable(db.get("suppressInitialDeveloperWarning") || false)