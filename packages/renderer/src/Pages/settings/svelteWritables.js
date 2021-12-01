
import { writable, get } from "svelte/store";
export { get };

const db_file_location = pathResolve(appInfo.userData, appInfo.isPackaged ? "db.json" : "db-dev.json" )
window.db = JSONdb(db_file_location)


window.unpackedLocation = appInfo.isPackaged ? pathJoin(dirname(appInfo.module), "resources/app.asar.unpacked/") : ROOT_DIR
const pyPath = pathJoin(unpackedLocation, "python3/python")
const pyScriptPath = pathJoin(unpackedLocation, "packages/renderer/dist/assets/python_files")


if(!db.get("pythonpath")) {db.set("pythonpath", pyPath)}
if(!db.get("pythonscript")) {db.set("pythonscript", pyScriptPath)}

export const pythonpath = writable(db.get("pythonpath"))
export const pythonscript = writable(db.get("pythonscript"))

export const pyVersion = writable("")
export const developerMode = writable(!appInfo.isPackaged)
export const suppressInitialDeveloperWarning = writable(db.get("suppressInitialDeveloperWarning") || false)
