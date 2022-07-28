import { exposeInMainWorld } from './exposeInMainWorld'
import fs from 'fs-extra'
import {promises as fsPromise} from 'fs'
import {tryF, isError} from 'ts-try'
import { promisify } from 'util'
import { syncTryCatcher, asyncTryCatcher } from './utils/trycatcher'
export const fsUtils = {
    mkdirSync: (dir: fs.PathLike) => fs.mkdirSync(dir),
    emptyDirSync: (dir: string) => fs.emptyDirSync(dir),
    ensureDirSync: (dir: string) => fs.ensureDirSync(dir),
    readdirSync: (dir: string, options = null) => {
        if(!(dir && fs.existsSync(dir))) return []
        return fs.readdirSync(dir, options)
    },
    
    ensureFileSync: (file: string) => fs.ensureFileSync(file),
    appendFileSync: (path: fs.PathOrFileDescriptor, data: string | Uint8Array) => fs.appendFileSync(path, data),
    rename: (oldPath: fs.PathLike, newPath: fs.PathLike, callback: (err: NodeJS.ErrnoException) => void) => {
        return fs.rename(oldPath, newPath, callback)
    },
    // readFileSync: (filename: fs.PathOrFileDescriptor) => fs.readFileSync(filename, 'utf-8'),
    readFileSync: (filename: fs.PathOrFileDescriptor) => tryF(() => fs.readFileSync(filename, 'utf-8')),
    existsSync: (location: fs.PathLike) => fs.existsSync(location),
    copySync: (src: string, dest: string) => fs.copySync(src, dest),
    writeFileSync: (path: fs.PathOrFileDescriptor, data: { toString: (arg0: string) => string | NodeJS.ArrayBufferView }) => {
        return fs.writeFileSync(path, data.toString('utf-8'))
    },
    removeSync: (remove: string) => fs.removeSync(remove),
    readJsonSync: (path: string) => tryF(() => fs.readJsonSync(path)),
    outputJsonSync: (filename: string, obj: Object, options = { spaces: 2 }) => {
        // const output = tryF(() => fs.outputJsonSync(filename, obj, options))
        // return output instanceof Error ? [null, output] : [output, null]
        return tryF(() => fs.outputJsonSync(filename, obj, options))
    },
    // readJsonSync: syncTryCatcher(fs.readJsonSync),
    // outputJsonSync: (file: string, obj: any, options = { spaces: 2 }) => {
    //     return syncTryCatcher(fs.outputJsonSync)(file, obj, options)
    // },
    isError: isError,
    tryF: tryF,
    // writeFile: asyncTryCatcher(promisify(fs.writeFile)),
    writeFile: (path: fs.PathLike, data: string) => tryF(fsPromise.writeFile(path, data, 'utf8')),
    readdir: (path: fs.PathLike) => tryF(fsPromise.readdir(path)),
    
    exists: async (path: fs.PathLike) => {
        return new Promise((resolve) => {
            fs.exists(path, (exists) => {
                resolve(exists)
            })
        })
    },
    readFile: async (path: number | fs.PathLike): Promise<[string | null, NodeJS.ErrnoException | null]> => {
        return new Promise((resolve) => {
            fs.readFile(path, 'utf-8', (err, data) => {
                if (err) resolve([null, err])
                resolve([data, null])
            })
        })
    },
    isFile: (path: fs.PathLike) => {
        try {
            return fs.statSync(path).isFile()
        } catch (e) {
            return false
        }
    },
    isDirectory: (path: fs.PathLike) => {
        try {
            return fs.statSync(path).isDirectory()
        } catch (e) {
            return false
        }
    },
    lstatSync: (location: fs.PathLike) => {
        const info = fs.lstatSync(location)
        return {
            isFile: () => info.isFile(),
            isDirectory: () => info.isDirectory(),
        }
    },
    createWriteStream: (path: fs.PathLike) => {
        const writer = fs.createWriteStream(path)
        return {
            write: (data: any) => writer.write(data),
            end: () => writer.end(),
            on: (key: string, callback: () => void) => writer.on(key, callback),
        }
    },
    createReadStream: (path: fs.PathLike) => {
        const reader = fs.createReadStream(path)    
        return {
            on: (key: string, callback: () => void) => reader.on(key, callback),
            pipe: (dest: any) => reader.pipe(dest),
        }
    }
}

exposeInMainWorld('fs', fsUtils)
