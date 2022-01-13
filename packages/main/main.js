import { app, BrowserWindow, ipcMain } from 'electron'
import path from "path"
import './security-restrictions.ts';
import unhandled from 'electron-unhandled';
import Store from 'electron-store'

Store.initRenderer();
const isSingleInstance = app.requestSingleInstanceLock();
if (!isSingleInstance) {
	app.quit();
	process.exit(0);
}

const env = import.meta.env;
console.table(env)

const ROOT_DIR = path.join(__dirname, "../../../")
const PKG_DIR = path.join(ROOT_DIR, "packages")
const RENDERER_DIR = path.join(PKG_DIR, "renderer")
console.table({ __dirname, ROOT_DIR, PKG_DIR, RENDERER_DIR })

async function createWindow() {
	const icon = path.join(RENDERER_DIR, env.DEV ? "public" : "dist", "assets/logo/icon.ico")
	const mainWindow = new BrowserWindow({
		width: 1200, height: 700, frame: true, icon, show: false,
		webPreferences: {
			preload: path.join(PKG_DIR, 'preload/dist/preload.cjs'),
			nodeIntegration: true
		}
	});

	import("./Menu")
	import("./dialogs")
	import("./autoupdate")

	mainWindow.on('ready-to-show', () => {
		mainWindow?.show();
		if (env.DEV) { mainWindow?.webContents.openDevTools(); }
	});

	const pageUrl = env.DEV
		? env.VITE_DEV_SERVER_URL
		: new URL(path.join(RENDERER_DIR, 'dist/index.html'), 'file://' + __dirname).toString();
	await mainWindow.loadURL(pageUrl);
}

app.whenReady().then(() => {
	createWindow()
	
	app.on('activate', () => {
		if (BrowserWindow.getAllWindows().length === 0) {
			createWindow()

			unhandled({showDialog: true})
		}
	})
}).catch(err => console.error(err))

app.on('window-all-closed', () => {
	if (process.platform !== 'darwin') {
		app.quit()
	}
})

ipcMain.on("appInfo", (event, arg) => {
	const appPathKeys = [
		"home",
		"appData",
		"userData",
		"cache",
		"temp",
		"exe",
		"module",
		"desktop",
		"documents",
		"downloads",
		"music",
		"pictures",
		"videos",
		"recent",
		"logs",
		"crashDumps"
	]
	const appInfo = { version: app.getVersion(), isPackaged: app.isPackaged }
	appPathKeys.forEach(key => appInfo[key] = app.getPath(key))
	appInfo.appPath = app.getAppPath()
	event.returnValue = appInfo
})
ipcMain.on("appVersion", (event, arg) => { event.returnValue = app.getVersion() })
