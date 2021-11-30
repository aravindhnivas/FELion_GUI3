const { app, BrowserWindow, ipcMain } = require('electron');
const path = require("path");

const isSingleInstance = app.requestSingleInstanceLock();
if (!isSingleInstance) {
  app.quit();
  process.exit(0);

}
const env = import.meta.env;
// const devMode = env.MODE === 'development'


const ROOT_DIR = path.join(__dirname, "../../../")
const PKG_DIR = path.join(ROOT_DIR, "packages")
const RENDERER_DIR = path.join(PKG_DIR, "renderer")

console.log({__dirname, ROOT_DIR, PKG_DIR, RENDERER_DIR, env})

async function createWindow() {
    const icon = path.join(RENDERER_DIR, env.DEV ? "public" : "dist", "assets/logo/icon.ico")

    const mainWindow = new BrowserWindow({
      width: 1200, height: 700, frame: true, icon, show: false,
      webPreferences: { 
        preload: path.join(PKG_DIR, 'preload/dist/preload.cjs'),
        nodeIntegration: true
       }
    });

    require("../Menu")
    require("../dialogs")
    require("../autoupdate")

    mainWindow.on('ready-to-show', () => {
      mainWindow?.show();
      if (env.DEV) {mainWindow?.webContents.openDevTools();}
    });
    

    env.DEV 
      ? await mainWindow.loadURL(env.VITE_DEV_SERVER_URL)
      : await mainWindow.loadFile(path.join(RENDERER_DIR, 'dist/index.html'))
    
}

app.whenReady().then(() => {
  createWindow()
  // mainWindow.show()
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
}).catch(err=>console.error(err))

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
