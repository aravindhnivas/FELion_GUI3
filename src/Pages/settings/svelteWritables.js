
import { writable, get } from "svelte/store";
export { get };
const db_file_location = pathResolve(appInfo.userData, appInfo.isPackaged ? "db.json" : "db-dev.json" )
window.db = JSONdb(db_file_location)
const mainLocation = appInfo.isPackaged ? appInfo.module : __dirname + "../"
const unpackedLocation =  pathResolve(mainLocation, appInfo.isPackaged ? "../resources/app.asar.unpacked/" : "../" )

if(!db.get("pythonpath")) {
    db.set("pythonpath", pathResolve(unpackedLocation, "python3/python"))
}
db.set("pythonscript", pathResolve(unpackedLocation, "static/assets/python_files"))

export const pythonpath = writable(db.get("pythonpath"))
export const pythonscript = writable(db.get("pythonscript"))

export const pyVersion = writable("")
export const developerMode = writable(!appInfo.isPackaged)
export const suppressInitialDeveloperWarning = writable(db.get("suppressInitialDeveloperWarning") || false)