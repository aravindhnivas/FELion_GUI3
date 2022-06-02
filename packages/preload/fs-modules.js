// import { contextBridge } from 'electron'
import { exposeInMainWorld } from './exposeInMainWorld'
import fs from 'fs-extra'
import { promisify } from 'util'
import { syncTryCatcher, asyncTryCatcher } from './utils/trycatcher'

// Export for types in contracts.d.ts
export const fsUtils = {
    mkdirSync: (dir) => fs.mkdirSync(dir),
    emptyDirSync: (dir) => fs.emptyDirSync(dir),
    ensureDirSync: (dir) => fs.ensureDirSync(dir),
    readdirSync: (dir = './', options = null) => fs.readdirSync(dir, options),
    ensureFileSync: (file) => fs.ensureFileSync(file),

    appendFileSync: (path, data) => fs.appendFileSync(path, data),
    rename: (oldPath, newPath, callback) => {
        return fs.rename(oldPath, newPath, callback)
    },
    readFileSync: (filename) => fs.readFileSync(filename, 'utf-8'),
    existsSync: (location) => fs.existsSync(location),
    copySync: (src, dest) => fs.copySync(src, dest),
    writeFileSync: (path, data) => {
        return fs.writeFileSync(path, data.toString('utf-8'))
    },
    removeSync: (remove) => fs.removeSync(remove),

    readJsonSync: syncTryCatcher(fs.readJsonSync),
    outputJsonSync: (file, obj, options = { spaces: 2 }) => {
        return syncTryCatcher(fs.outputJsonSync)(file, obj, options)
    },
    writeFile: asyncTryCatcher(promisify(fs.writeFile)),
    readdir: asyncTryCatcher(promisify(fs.readdir)),
    exists: async (path) => {
        return new Promise((resolve) => {
            fs.exists(path, (exists) => {
                resolve(exists)
            })
        })
    },
    readFile: async (path) => {
        return new Promise((resolve) => {
            fs.readFile(path, 'utf-8', (err, data) => {
                if (err) resolve([null, err])
                resolve([data, null])
            })
        })
    },

    isFile: (path) => {
        try {
            return fs.statSync(path).isFile()
        } catch (e) {
            return false
        }
    },
    isDirectory: (path) => {
        try {
            return fs.statSync(path).isDirectory()
        } catch (e) {
            return false
        }
    },

    lstatSync: (location) => {
        const info = fs.lstatSync(location)
        return {
            isFile: () => info.isFile(),
            isDirectory: () => info.isDirectory(),
        }
    },
    createWriteStream: (path) => {
        const writer = fs.createWriteStream(path)
        return {
            write: (data) => writer.write(data),
            end: () => writer.end(),
            on: (key, callback) => writer.on(key, callback),
        }
    },
}

// contextBridge.exposeInMainWorld('fs', fsUtils)
exposeInMainWorld('fs', fsUtils)
