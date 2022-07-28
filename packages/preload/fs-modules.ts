import { exposeInMainWorld } from './exposeInMainWorld'
import fs from 'fs-extra'
import {promises as fsPromise} from 'fs'
import {tryF, isError} from 'ts-try'
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
    readFileSync: (filename: fs.PathOrFileDescriptor) => tryF(() => fs.readFileSync(filename, 'utf-8')),
    existsSync: (location: fs.PathLike) => fs.existsSync(location),
    copySync: (src: string, dest: string) => fs.copySync(src, dest),
    writeFileSync: (path: fs.PathOrFileDescriptor, data: string) => {
        return tryF(() => fs.writeFileSync(path, data))
    },
    removeSync: (path: string) => tryF(() => fs.removeSync(path)),
    readJsonSync: (path: string) => tryF(() => fs.readJsonSync(path)),
    outputJsonSync: (filename: string, obj: Object, options = { spaces: 2 }) => {
        return tryF(() => fs.outputJsonSync(filename, obj, options))
    },
    isError: isError,
    tryF: tryF,
    writeFile: (path: fs.PathLike, data: string) => tryF(fsPromise.writeFile(path, data, 'utf8')),
    readdir: (path: fs.PathLike) => tryF(fsPromise.readdir(path)),
    readFile: async (path: fs.PathLike) => tryF(fsPromise.readFile(path, 'utf-8')),
    isFile: (path: fs.PathLike) => {
        const output = tryF(() => fs.statSync(path).isFile())
        return isError(output) ? false : output
    },
    isDirectory: (path: fs.PathLike) => {
        const output = tryF(() => fs.statSync(path).isDirectory())
        return isError(output) ? false : output
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
