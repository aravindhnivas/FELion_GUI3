import { BrowserWindow, ipcMain, Menu, MenuItem, app } from 'electron'

let rightClickPosition
let currentWindow

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

menu.append(new MenuItem({ label: 'DevTools', role: 'toggledevtools' }))

menu.append(
    new MenuItem({
        label: 'Inspect Element',
        click() {
            currentWindow.inspectElement(rightClickPosition.x, rightClickPosition.y)
        },
    })
)

ipcMain.on('contextmenu', (event, args) => {
    const webContents = event.sender
    currentWindow = BrowserWindow.fromWebContents(webContents)
    rightClickPosition = args
    menu.popup(currentWindow)
})
