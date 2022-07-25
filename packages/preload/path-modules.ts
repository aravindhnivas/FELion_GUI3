import { exposeInMainWorld } from './exposeInMainWorld'
import { resolve, join, dirname, basename } from 'path'
export const path = {
    resolve,
    join,
    dirname,
    basename,
}
exposeInMainWorld('path', path)
