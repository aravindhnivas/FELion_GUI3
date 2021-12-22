
import { writable, get } from "svelte/store";
export { get };

const db_file_location = pathResolve(appInfo.userData, appInfo.isPackaged ? "db.json" : "db-dev.json" )
window.db = JSONdb(db_file_location)

const pyPath = pathJoin(ROOT_DIR, "python3/python")
const pyScriptPath = pathJoin(ROOT_DIR, "resources/python_files")

if(!db.get("pythonpath")) {db.set("pythonpath", pyPath)}
if(!db.get("pythonscript")) {db.set("pythonscript", pyScriptPath)}

export const pythonpath = writable(db.get("pythonpath"))
export const pythonscript = writable(db.get("pythonscript"))

export const pyVersion = writable("")
export const developerMode = writable(db.get("developerMode") ?? appInfo.isPackaged)
console.log("developerMode: ", db.get("developerMode"), get(developerMode))
export const suppressInitialDeveloperWarning = writable(db.get("suppressInitialDeveloperWarning") || false)
