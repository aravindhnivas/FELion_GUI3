const { app, BrowserWindow, ipcMain } = require('electron');
const path = require("path");

function createWindow() {
  let icon = path.resolve(__dirname, "static/assets/logo/win/icon.ico")
  const mainWindow = new BrowserWindow({
    width: 1200, height: 700, frame: true, icon,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), nodeIntegration: true }
  });

  mainWindow.loadFile('static/index.html');
  ipcMain.on("appVersion", (event, arg) => {event.returnValue = app.getVersion()})

  require("./main/Menu")
  require("./main/dialogs")
  require("./main/autoupdate")
}


app.whenReady().then(() => {
  createWindow()
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
