import { contextBridge, ipcRenderer } from 'electron'
import { versions } from "process"
import path from "path"
import fs from "fs-extra"
const env = import.meta.env;
contextBridge.exposeInMainWorld("env", env)

contextBridge.exposeInMainWorld("versions", versions)
export const appInfo = ipcRenderer.sendSync("appInfo", null)
contextBridge.exposeInMainWorld("appInfo", appInfo)
export const { isPackaged } = appInfo

export const ROOT_DIR = isPackaged ? path.dirname(appInfo.module) : path.join(__dirname, "../../../")
export const PKG_DIR = path.join(ROOT_DIR, "packages")
export const RENDERER_DIR = path.join(PKG_DIR, "renderer")

contextBridge.exposeInMainWorld("ROOT_DIR", ROOT_DIR)
export const publicDirectory = path.join(RENDERER_DIR, isPackaged ? "dist" : "public")
contextBridge.exposeInMainWorld("__dirname", publicDirectory)
console.table({ ROOT_DIR, PKG_DIR, RENDERER_DIR, publicDirectory })
console.table(env)

contextBridge.exposeInMainWorld("appVersion", ipcRenderer.sendSync('appVersion', null))

fs.ensureDirSync(path.join(appInfo.userData, "config"))