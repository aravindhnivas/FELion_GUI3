import { contextBridge } from 'electron'
import path from 'path'

contextBridge.exposeInMainWorld('pathResolve', path.resolve)
contextBridge.exposeInMainWorld('pathJoin', path.join)
contextBridge.exposeInMainWorld('basename', path.basename)
contextBridge.exposeInMainWorld('extname', path.extname)
contextBridge.exposeInMainWorld('dirname', path.dirname)
