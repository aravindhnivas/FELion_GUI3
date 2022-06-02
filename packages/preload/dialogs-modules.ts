import { ipcRenderer} from 'electron'
import { exposeInMainWorld } from './exposeInMainWorld'
import type {OpenDialogSyncOptions, MessageBoxOptions, MessageBoxReturnValue } from 'electron'

export const dialogs = {

    showOpenDialogSync: (args: OpenDialogSyncOptions): string[] => ipcRenderer.sendSync('showOpenDialogSync', args),
    showMessageBox: async (args: MessageBoxOptions): Promise<MessageBoxReturnValue> => ipcRenderer.invoke('showMessageBox', args),
}

export const reload = () => ipcRenderer.invoke('reload')
export const relaunch = () => ipcRenderer.invoke('relaunch')

exposeInMainWorld('dialogs', dialogs)
exposeInMainWorld('reload', reload)
exposeInMainWorld('relaunch', relaunch)
