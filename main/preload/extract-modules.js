
const { contextBridge } = require('electron')
const { extractFull } = require('node-7z-forall')

contextBridge.exposeInMainWorld("extractFull", (zipfile, folder, opts={})=>{
    return extractFull(zipfile, folder, opts)
})
