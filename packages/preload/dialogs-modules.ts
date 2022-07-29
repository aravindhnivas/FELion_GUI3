import { ipcRenderer} from 'electron'
import { exposeInMainWorld } from './exposeInMainWorld'
import type {OpenDialogSyncOptions, MessageBoxOptions, MessageBoxReturnValue } from 'electron'

export const dialogs = {

    showOpenDialogSync: (args: OpenDialogSyncOptions): string[] => ipcRenderer.sendSync('showOpenDialogSync', args),
    showMessageBox: async (args: MessageBoxOptions): Promise<MessageBoxReturnValue> => ipcRenderer.invoke('showMessageBox', args),
}

export const reload = () => ipcRenderer.invoke('reload')
export const relaunch = () => ipcRenderer.invoke('relaunch')

export function browse({ filetype = '', dir = true, multiple = false } = {}) {
    
    const properties: Array<"openDirectory" | "openFile" | "multiSelections"> = []
    
    const type = dir ? 'openDirectory' : 'openFile'
    properties.push(type)
    
    if (multiple) {
        properties.push('multiSelections')
    }
    
    const options: OpenDialogSyncOptions = {
        filters: [
            { name: filetype, extensions: [`*${filetype}`] },
            { name: 'All Files', extensions: ['*'] },
        ],
        properties,
    }

    const { showOpenDialogSync } = dialogs
    console.table(options)
    console.log('Directory: ', dir)
    console.log('multiSelections: ', multiple)
    const result = showOpenDialogSync(options) ?? ['']
    return result
}

exposeInMainWorld('dialogs', dialogs)
exposeInMainWorld('reload', reload)
exposeInMainWorld('relaunch', relaunch)
exposeInMainWorld('browse', browse)
