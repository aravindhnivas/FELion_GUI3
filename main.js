const { app, BrowserWindow, dialog } = require('electron');
const {showMessageBoxSync} = dialog;
const path = require("path");
const log = require('electron-log');
const {autoUpdater} = require("electron-updater");
autoUpdater.logger = log;
autoUpdater.logger.transports.file.level = 'info';
log.info('App starting...');

let mainWindow;
function createWindow() {


  let icon = path.resolve(__dirname, "static/assets/logo/win/icon.ico")
  mainWindow = new BrowserWindow({
    width: 1200, height: 700, frame: true, icon,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), nodeIntegration: true }
  });


  mainWindow.loadFile('static/index.html');
}

app.whenReady().then(() => {
  createWindow()
  require("./main/Menu")
  require("./main/dialogs")
  if(app.isPackaged) {autoUpdater.checkForUpdates();}
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})



autoUpdater.on('checking-for-update', () => {log.info("checking-for-update");})
autoUpdater.on('update-available', (info) => {log.info(info);})
autoUpdater.on('update-not-available', (info) => {log.info(info);})
autoUpdater.on('error', (err) => {log.error(err)})
autoUpdater.on('download-progress', (progressObj) => {
  let log_message = "Download speed: " + progressObj.bytesPerSecond;
  log_message = log_message + ' - Downloaded ' + progressObj.percent + '%';
  log_message = log_message + ' (' + progressObj.transferred + "/" + progressObj.total + ')';
  console.log(log_message)

})
autoUpdater.on('update-downloaded', async (info) => {
  log.info(info);
  const restartArgs = { title: "FELion_GUI3", type: "info", message: "Update donwloaded", buttons: ["Restart and Install", "Later"] }

  const response = await showMessageBoxSync(mainWindow, restartArgs)
  if(response === 0) {
    autoUpdater.quitAndInstall();  
  }
})