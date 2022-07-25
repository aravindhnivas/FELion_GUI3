import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'
import './security-restrictions.ts'
import unhandled from 'electron-unhandled'
import { ROOT_DIR, RENDERER_DIR, PKG_DIR } from './definedEnv'
import { startServer } from './felionpyServer'
import fs from 'fs-extra'
const isSingleInstance = app.requestSingleInstanceLock()

if (!isSingleInstance) {
    app.quit()
    process.exit(0)
}

const env = import.meta.env
console.table(env)

async function createWindow() {
    const icon = path.join(app.getAppPath(), 'packages/renderer', env.DEV ? 'public' : 'dist', 'assets/logo/icon.ico')
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 700,
        frame: true,
        icon,
        show: false,
        webPreferences: {
            preload: path.join(app.getAppPath(), 'packages/preload/dist/preload.cjs'),
            nodeIntegration: true,
        },
    })

    import('./Menu')
    import('./dialogs')
    import('./autoupdate')

    const webContents = mainWindow?.webContents
    startServer(webContents)

    mainWindow.on('ready-to-show', () => {
        mainWindow?.show()
        if (env.DEV) {
            mainWindow?.webContents.openDevTools()
        }
    })

    const pageUrl = env.DEV
        ? env.VITE_DEV_SERVER_URL
        : new URL(path.join(app.getAppPath(), 'packages/renderer/dist/index.html'), 'file://' + __dirname).toString()

    await mainWindow.loadURL(pageUrl)
}

app.whenReady()
    .then(() => {
        fs.emptyDirSync(app.getPath('logs'))
        createWindow()
        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) {
                createWindow()
                unhandled({ showDialog: true })
            }
        })
    })
    .catch((err) => console.error(err))

app.on('window-all-closed', async () => {

    if (process.platform !== 'darwin') {
        app.quit()
    }

    console.log('Application closed')
})

ipcMain.on('appInfo', (event, _arg) => {

    const appPathKeys = [
        'appData',
        'userData',
        'cache',
        'temp',
        'exe',
        'module',
        'logs',
        'crashDumps',
    ]
    const appInfo = {
        version: app.getVersion(),
        isPackaged: app.isPackaged,
        platform: process.platform,
    }
    appPathKeys.forEach((key) => (appInfo[key] = app.getPath(key)))
    appInfo.appPath = app.getAppPath()
    appInfo.ROOT_DIR = ROOT_DIR
    appInfo.RENDERER_DIR = RENDERER_DIR
    appInfo.PKG_DIR = PKG_DIR
    event.returnValue = appInfo
})

ipcMain.on('appVersion', (event, _arg) => {
    event.returnValue = app.getVersion()
})

ipcMain.handle('startServer', async (event, _args) => {
    try {
        console.log('starting server')
        const webContents = event.sender
        const response = await startServer(webContents)
        return response
    } catch (error) {
        console.error(error)
        return error
    }
})
