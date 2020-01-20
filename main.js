const {app, BrowserWindow} = require('electron');

let mainWindow;

function createWindow () {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    frame: false,
    webPreferences: {
      nodeIntegration: true, nativeWindowOpen: true
    },

    icon: 'icon.png',
    backgroundColor: "#46307d"
  });

  mainWindow.loadFile('public/index.html');

  mainWindow.on('closed', function () {
    mainWindow = null
  });

  
  mainWindow.webContents.on('new-window', (event, url, frameName, disposition, options, additionalFeatures) => {

    event.preventDefault()
      Object.assign(options, {
        backgroundColor: "#fafafa",
        modal: false,
        frame: true,
        parent: mainWindow,
        width: 1000,
        height: 800
      })
      event.newGuest = new BrowserWindow(options)

      // return event.newGuest;
  })
}

app.on('ready', createWindow);

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
})

app.on('activate', function () {
  if (mainWindow === null) createWindow();
})
