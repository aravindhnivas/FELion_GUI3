const { app, BrowserWindow, ipcMain } = require('electron');
const path = require("path");

const ROOT_DIR = path.join(__dirname, "../../")
const PKG_DIR = path.join(ROOT_DIR, "packages")
const RENDERER_DIR = path.join(PKG_DIR, "renderer")
console.log({__dirname, ROOT_DIR, PKG_DIR, RENDERER_DIR})

function createWindow() {
  let icon = path.join(RENDERER_DIR, "public/assets/logo/win/icon.ico")
  const mainWindow = new BrowserWindow({
    width: 1200, height: 700, frame: true, icon, show: false,

    webPreferences: { preload: path.join(PKG_DIR, 'preload/preload.js'), nodeIntegration: true }
  });
  mainWindow.loadFile(path.join(RENDERER_DIR, 'index.html'));

  require("./Menu")
  require("./dialogs")
  require("./autoupdate")
  mainWindow.webContents.openDevTools(true)
  return mainWindow
}

app.whenReady().then(() => {
  const mainWindow = createWindow()
  mainWindow.show()
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

ipcMain.on("appInfo", (event, arg) => {
  const appPathKeys = ["home" ,"appData" ,"userData" ,"cache" ,"temp" ,"exe" ,"module" ,"desktop" ,"documents" ,"downloads" ,"music" ,"pictures" ,"videos" ,"recent" ,"logs" ,"crashDumps"]
  const appInfo = {version: app.getVersion(), isPackaged: app.isPackaged}
  appPathKeys.forEach(key => appInfo[key] = app.getPath(key) )
  event.returnValue = appInfo
})
ipcMain.on("appVersion", (event, arg) => {event.returnValue = app.getVersion()})
