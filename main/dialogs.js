
const { ipcMain, dialog, BrowserWindow } = require('electron');
const {showMessageBoxSync, showOpenDialogSync} = dialog
const mainWindow = BrowserWindow.getAllWindows()[0]
ipcMain.handle('showOpenDialogSync', async (event, args) => {
    const result = await showOpenDialogSync(mainWindow, args)
    return result
})
ipcMain.handle('showMessageBoxSync', async (event, args) => {
    const result = await showMessageBoxSync(mainWindow, args)
    return result
})

ipcMain.handle('reload',  () => mainWindow.reload() )