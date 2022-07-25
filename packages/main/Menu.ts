import { BrowserWindow, ipcMain, Menu, MenuItem, app } from 'electron'

let rightClickPosition: { x: number, y: number } = { x: 0, y: 0 }
let currentWindow: BrowserWindow

const menu = new Menu()
Menu.setApplicationMenu(menu)

menu.append(new MenuItem({ label: 'Reload', role: 'reload' }))
menu.append(
    new MenuItem({
        label: 'Relaunch',
        click() {
            app.relaunch({ args: process.argv.slice(1).concat(['--relaunch']) })
            app.exit(0)
        },
    })
)

menu.append(new MenuItem({ label: 'DevTools', role: 'toggleDevTools' }))

menu.append(
    new MenuItem({
        label: 'Inspect Element',
        click() {
            currentWindow.webContents.inspectElement(rightClickPosition.x, rightClickPosition.y)
        },
    })
)

ipcMain.on('contextmenu', (event, args) => {
    const webContents = event.sender
    currentWindow = <BrowserWindow>BrowserWindow.fromWebContents(webContents)
    rightClickPosition = args
    menu.popup()
})
