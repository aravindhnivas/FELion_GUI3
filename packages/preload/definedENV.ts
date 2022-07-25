import { contextBridge, ipcRenderer, shell } from 'electron'
import {exposeInMainWorld} from './exposeInMainWorld'
import { versions, platform } from 'process'
import * as path from 'path'
import * as fs from 'fs-extra'
const env = import.meta.env
contextBridge.exposeInMainWorld('env', env)

export {platform, versions}
contextBridge.exposeInMainWorld('versions', versions)
export const appInfo = ipcRenderer.sendSync('appInfo', null)
exposeInMainWorld('appInfo', appInfo)

export const { isPackaged, ROOT_DIR } = appInfo
exposeInMainWorld('ROOT_DIR', ROOT_DIR)

export const appVersion: string = ipcRenderer.sendSync('appVersion', null)
exposeInMainWorld('appVersion', appVersion)

export const shellUtils = {
    showItemInFolder: (item: string) => {
        shell.showItemInFolder(item)
    },
    openExternal: (url: string, options: Electron.OpenExternalOptions) => {
        shell.openExternal(url, options)
    }
}


exposeInMainWorld('shell', shellUtils)
exposeInMainWorld('platform', platform)
exposeInMainWorld('isPackaged', isPackaged)

fs.ensureDirSync(path.join(appInfo.userData, 'config'))
