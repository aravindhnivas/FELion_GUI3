
const { BrowserWindow, dialog, app, ipcMain } = require('electron');
const {autoUpdater} = require("electron-updater");
const logger = require('electron-log');

const mainWindow = BrowserWindow.getAllWindows()[0]
const {showMessageBoxSync} = dialog;

autoUpdater.logger = logger;
autoUpdater.logger.transports.file.level = 'info';
logger.info('App starting...');
if(app.isPackaged) {autoUpdater.checkForUpdates();}

ipcMain.handle("checkupdate", () => autoUpdater.checkForUpdates())

const updateLog = (info) => {logger.info(info); mainWindow.webContents.send("update-log", info)}
autoUpdater.on('checking-for-update', () => updateLog("checking-for-update"))
autoUpdater.on('update-available', (info) => {updateLog(info);})
autoUpdater.on('update-not-available', (info) => {updateLog(info);})
autoUpdater.on('error', (err) => {logger.error(err); mainWindow.webContents.send("update-log-error", err)})
autoUpdater.on('download-progress', (progressObj) => {
  const log_message = "Download speed: " + progressObj.bytesPerSecond;
  log_message = log_message + ' - Downloaded ' + progressObj.percent + '%';
  log_message = log_message + ' (' + progressObj.transferred + "/" + progressObj.total + ')';
  console.log(log_message)
})

autoUpdater.on('update-downloaded', async (info) => {
    logger.info(info);
    const restartArgs = { 
        title: "FELion_GUI3", type: "info", message: "Update donwloaded",
        buttons: ["Restart and Install", "Later"]
     }
    const response = await showMessageBoxSync(mainWindow, restartArgs)
    if(response === 0) {
        autoUpdater.quitAndInstall();  
    }
})