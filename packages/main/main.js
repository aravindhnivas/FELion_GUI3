import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'
import './security-restrictions.ts'
import unhandled from 'electron-unhandled'
import { ROOT_DIR, RENDERER_DIR, PKG_DIR } from './definedEnv'
import { startServer } from './felionpyServer'
const isSingleInstance = app.requestSingleInstanceLock()

if (!isSingleInstance) {
    app.quit()
    process.exit(0)
}

// let controller = new AbortController()
const env = import.meta.env
console.table(env)
console.table({ __dirname, ROOT_DIR, PKG_DIR, RENDERER_DIR })

async function createWindow() {
    const icon = path.join(
        RENDERER_DIR,
        env.DEV ? 'public' : 'dist',
        'assets/logo/icon.ico'
    )
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 700,
        frame: true,
        icon,
        show: false,
        webPreferences: {
            preload: path.join(PKG_DIR, 'preload/dist/preload.cjs'),
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
        : new URL(
              path.join(RENDERER_DIR, 'dist/index.html'),
              'file://' + __dirname
          ).toString()

    await mainWindow.loadURL(pageUrl)
}

app.whenReady()
    .then(() => {
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

ipcMain.on('appInfo', (event, arg) => {
    const appPathKeys = [
        'home',
        'appData',
        'userData',
        'cache',
        'temp',
        'exe',
        'module',
        'desktop',
        'documents',
        'downloads',
        'music',
        'pictures',
        'videos',
        'recent',
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
    event.returnValue = appInfo
})

ipcMain.on('appVersion', (event, arg) => {
    event.returnValue = app.getVersion()
})

ipcMain.handle('startServer', async (event, args) => {
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
