import { contextBridge, ipcRenderer } from 'electron'
import {exposeInMainWorld} from './exposeInMainWorld'
import { versions } from 'process'
import path from 'path'
import fs from 'fs-extra'

const env = import.meta.env
contextBridge.exposeInMainWorld('env', env)

contextBridge.exposeInMainWorld('versions', versions)
export const appInfo = ipcRenderer.sendSync('appInfo', null)
exposeInMainWorld('appInfo', appInfo)

export const { isPackaged } = appInfo
export const ROOT_DIR = isPackaged ? path.dirname(appInfo.module) : path.join(__dirname, '../../../')
exposeInMainWorld('ROOT_DIR', ROOT_DIR)

export const PKG_DIR = path.join(ROOT_DIR, 'packages')
export const RENDERER_DIR = path.join(PKG_DIR, 'renderer')

export const publicDirectory = path.join(RENDERER_DIR, isPackaged ? 'dist' : 'public')
exposeInMainWorld('__dirname', publicDirectory)
export const appVersion: string = ipcRenderer.sendSync('appVersion', null)
exposeInMainWorld('appVersion', appVersion)
fs.ensureDirSync(path.join(appInfo.userData, 'config'))