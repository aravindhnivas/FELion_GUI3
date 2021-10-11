const { BrowserWindow, ipcMain, Menu, MenuItem, app } = require('electron');

const menu = new Menu()
const mainWindow = BrowserWindow.getAllWindows()[0]

Menu.setApplicationMenu(menu)
let rightClickPosition;

menu.append(new MenuItem({ label: 'Reload', role:"reload" }))
menu.append(new MenuItem({ label: 'Relaunch', click() {
    app.relaunch({ args: process.argv.slice(1).concat(['--relaunch']) })
    app.exit(0)

    }
}))

menu.append(new MenuItem({ label: 'DevTools', role: 'toggledevtools' }))



menu.append(new MenuItem({ label: "Inspect Element", 
    click() {  mainWindow.inspectElement(rightClickPosition.x, rightClickPosition.y) } 
}))

ipcMain.handle("contextmenu",  (event, args) => {
    rightClickPosition = args
    menu.popup(mainWindow)
})