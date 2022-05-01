import { contextBridge } from 'electron'
import logger from 'electron-log'

const { log, error, warn, info, verbose, debug, silly } = logger
const newconsole = { log, error, warn, info, verbose, debug, silly }
contextBridge.exposeInMainWorld('logger', newconsole)
// window.console = newconsole
// contextBridge.exposeInMainWorld("console", {log, error, warn, info, verbose, debug, silly})
