
const { contextBridge } = require('electron')
const fs = require("fs-extra")

contextBridge.exposeInMainWorld("readdirSync", (dir="./", options=null)=>fs.readdirSync(dir, options))
contextBridge.exposeInMainWorld("readFileSync", (filename)=>fs.readFileSync(filename, "utf-8"))
contextBridge.exposeInMainWorld("existsSync", (location)=>fs.existsSync(location))

contextBridge.exposeInMainWorld("lstatSync", (location)=>{
    const info = fs.lstatSync(location)
    return {
        isFile: () => info.isFile(),

        isDirectory: () => info.isDirectory()

    }


})
contextBridge.exposeInMainWorld("writeFile", (filename, contents, callback)=>{
    return fs.writeFile(filename, contents, "utf8", callback)
})

contextBridge.exposeInMainWorld("fs", {
    mkdirSync: (dir) => fs.mkdirSync(dir),
    emptyDirSync: (dir) => fs.emptyDirSync(dir),
    ensureDirSync: (dir) => fs.ensureDirSync(dir),
    readdirSync: (dir="./", options=null) => fs.readdirSync(dir, options),
    ensureFileSync: (file) => fs.ensureFileSync(file),
    appendFileSync: (path, data) => fs.appendFileSync(path, data),
    rename: (oldPath, newPath, callback) => fs.rename(oldPath, newPath, callback),
    readFileSync: (filename) => fs.readFileSync(filename, "utf-8"),
    existsSync: (location) => fs.existsSync(location),
    copySync: (src, dest) => fs.copySync(src, dest),
    writeFileSync: (path, data) => fs.writeFileSync(path, data.toString("utf-8") ),
    removeSync: (remove) => fs.removeSync(remove),
    readJsonSync: (jsonFile) => fs.readJsonSync(jsonFile),
    outputJsonSync: (file, obj) => fs.outputJsonSync(file, obj),
    createWriteStream: (path) => {
        const writer = fs.createWriteStream(path)
        return {
            write: (data) => writer.write(data),
            end: () => writer.end(),
            on: (key, callback) => writer.on(key, callback)
        }
    },
    lstatSync: (location) => {
        const info = fs.lstatSync(location)
        return {
            isFile: () => info.isFile(),
            isDirectory: () => info.isDirectory()
        }
    
    }
})



contextBridge.exposeInMainWorld("mkdirSync", (dir)=>fs.mkdirSync(dir))
contextBridge.exposeInMainWorld("createWriteStream", (path)=>fs.createWriteStream(path))
contextBridge.exposeInMainWorld("rename", (oldPath, newPath, callback)=>fs.rename(oldPath, newPath, callback))