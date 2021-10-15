
const { app, ipcMain, dialog, BrowserWindow} = require('electron');
const fs = require("fs-extra");
const path = require("path")
const { exec } = require('child_process')
const {showMessageBoxSync} = dialog;
const mainWindow = BrowserWindow.getAllWindows()[0];

ipcMain.handle("update", async (event, args=null) => {
    const TEMP = path.resolve(app.getPath("temp"), "FELion")
    let src, dest;
    if(args) {

        ({src, dest} = args);
    } else {
        const zipfolder = path.resolve(TEMP, "update")
        const zipfolderContainer = fs.readdirSync(zipfolder)
        src = zipfolderContainer.length > 1 ? zipfolder : path.join(zipfolder, zipfolderContainer[0])
        dest = path.dirname(app.getPath("exe"))

    }
    console.log({src, dest})
    fs.readdirSync(dest).forEach(oldname => {
        try {
            const newName = oldname+".delete"
            fs.renameSync(oldname, newName)
        } catch (error) {
            console.log(error)
        }
    })
    
    fs.copySync(src, dest)
    fs.readdirSync(dest).forEach(name => {
        if(name.includes(".delete")) fs.removeSync(name)
    })
    const restartArgs = { title: "FELion_GUI3", type: "info", message: "Update donwloaded", buttons: ["Restart and Install", "Later"] }
    const response = await showMessageBoxSync(mainWindow, restartArgs)
    if(response === 0) {
        app.relaunch({ execPath : process.argv.slice(1).concat(['--relaunch']) })
        app.exit(0)
    }
})