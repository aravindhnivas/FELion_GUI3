const { app, BrowserWindow } = require('electron');
let mainWindow;
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 700,
    frame: false,
    webPreferences: {
      nodeIntegration: true, nativeWindowOpen: true, webviewTag: true, nodeIntegrationInWorker: true
    },
    // icon: 'icon.png',
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