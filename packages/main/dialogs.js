
import { ipcMain, dialog, BrowserWindow, app } from 'electron'
// const {showMessageBoxSync, showOpenDialogSync} = dialog
const mainWindow = BrowserWindow.getAllWindows()[0]
ipcMain.on('showOpenDialogSync', (event, args) => {
    event.returnValue = dialog.showOpenDialogSync(mainWindow, args)
    // return result
})
ipcMain.handle('showMessageBox', async (event, args) => {
    const result = await dialog.showMessageBox(mainWindow, args)
    return result
})

ipcMain.handle('reload',  () => mainWindow.reload())
ipcMain.handle('relaunch',  () => {
    app.relaunch({ args: process.argv.slice(1).concat(['--relaunch']) })
    app.exit(0)
} )