
const { contextBridge } = require('electron')
const fs = require("fs-extra")

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

    writeFile:  (filename, contents, callback)=>fs.writeFile(filename, contents, "utf8", callback),
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
    
    },
    createReadStream: (inFile) => {
        const reader = fs.createReadStream(inFile)
        return {
            pipe: (callback) => reader.pipe(callback)
        }
    }
})