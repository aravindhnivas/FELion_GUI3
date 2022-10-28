import { BrowserWindow, dialog, app, ipcMain } from 'electron'
import { autoUpdater } from 'electron-updater'
import logger from 'electron-log'

const mainWindow = BrowserWindow.getAllWindows()[0]
autoUpdater.logger = logger

if (app.isPackaged) {
    try {
        autoUpdater.checkForUpdates()
    } catch (error) {
        logger.error(error)
    }
}

logger.info('App starting...')

ipcMain.handle('checkupdate', () => {
    if (downloading) return updateLog('Downloading update...')
    autoUpdater.checkForUpdates()
})

ipcMain.handle('quitAndInstall', () => {
    // if (!updateReadyToInstall) return updateLog('update not ready to install')
    autoUpdater.quitAndInstall()
})

const updateLog = (info: string) => {
    logger.info(info)
    mainWindow.webContents.send('update-log', info)
}

autoUpdater.on('checking-for-update', () => {
    mainWindow.webContents.send('db:update', {
        key: 'update-status',
        value: 'checking-for-update',
    })
    updateLog('checking-for-update' + '\n-----------\n')
})

autoUpdater.on('update-available', (info) => {
    mainWindow.webContents.send('db:update', {
        key: 'update-status',
        value: 'update-available',
    })
    updateLog('update-available: \n' + JSON.stringify(info) + '\n-----------\n')
})

autoUpdater.on('update-not-available', (info) => {
    mainWindow.webContents.send('db:update', {
        key: 'update-status',
        value: 'update-not-available',
    })
    updateLog('update-not-available ' + JSON.stringify(info) + '\n-----------\n')
})

autoUpdater.on('error', (err) => {
    downloading = false
    logger.error(err)
    mainWindow.webContents.send('db:update', {
        key: 'update-status',
        value: 'download-error',
    })
    mainWindow.webContents.send('db:update', {
        key: 'updateError',
        value: err?.stack,
    })
})

let downloading = false

autoUpdater.on('download-progress', (progressObj) => {
    downloading = true
    let log_message = 'Download speed: ' + progressObj.bytesPerSecond
    log_message = log_message + ' - Downloaded ' + progressObj.percent + '%'
    log_message = log_message + ' (' + progressObj.transferred + '/' + progressObj.total + ')'
    updateLog('download-progress: ' + log_message + '\n-----------\n')
    mainWindow.webContents.send('update-progress', progressObj)
})

// let updateReadyToInstall = false

autoUpdater.on('update-downloaded', async (info) => {
    downloading = false
    // updateReadyToInstall = true
    logger.info('update-downloaded' + info)
    mainWindow.webContents.send('db:update', {
        key: 'update-status',
        value: 'update-downloaded',
    })

    const restartArgs = {
        title: 'FELion_GUI3',
        type: 'info',
        message: 'Update donwloaded',
        buttons: ['Restart and Install', 'Later in 1 hr', 'Cancel'],
    }

    const message = await dialog.showMessageBox(mainWindow, restartArgs)
    if (message.response === 0) {
        // updateReadyToInstall = false
        autoUpdater.quitAndInstall()
    } else if (message.response === 1) {
        mainWindow.webContents.send('db:update', {
            key: 'delayupdate',
            value: true,
        })
    }
})
