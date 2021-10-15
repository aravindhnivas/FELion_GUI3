
const { app, ipcMain, dialog, BrowserWindow} = require('electron');
const fs = require("fs-extra");
const path = require("path")
const {showMessageBoxSync} = dialog;

const mainWindow = BrowserWindow.getAllWindows()[0];

ipcMain.handle("update", async (event) => {
    const TEMP = path.resolve(app.getPath("temp"), "FELion")
    const zipfolder = path.resolve(TEMP, "update")
    const zipfolderContainer = fs.readdirSync(zipfolder)

    const relativeAppPath = "resources/app"
    const fullPath = zipfolderContainer.length > 1 ? zipfolder : path.join(zipfolder, zipfolderContainer[0])
    const src = path.join(fullPath, relativeAppPath)



    
    // const dest = path.dirname(app.getPath("exe"))
    const dest = app.getAppPath()
    console.log({src, dest})
    fs.copySync(src, dest)
    const restartArgs = { title: "FELion_GUI3", type: "info", message: "Update donwloaded", buttons: ["Restart and Install", "Later"] }
    
    const response = await showMessageBoxSync(mainWindow, restartArgs)
    if(response === 0) {
        app.relaunch({ args : process.argv.slice(1).concat(['--relaunch']) })
        app.exit(0)
    }
})