const { app, BrowserWindow } = require('electron');
const path = require("path");
let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200, height: 700, frame: false, icon: path.resolve(__dirname, "assets/logo/felion_icon.icns"),
    webPreferences: {
      nodeIntegration: true, contextIsolation: false, nativeWindowOpen: true, webviewTag: true, nodeIntegrationInWorker: true, enableRemoteModule: true
    },
    backgroundColor: "#46307d"
  });
  
  mainWindow.loadFile('static/index.html');
  mainWindow.on('closed', function () { mainWindow = null })
}

app.on('ready', createWindow);
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
})

app.on('activate', function () { if (mainWindow === null) createWindow() })