import { exposeInMainWorld } from './exposeInMainWorld'
// import path from 'path'
import {resolve, join, dirname, basename, extname} from 'path'
export const path = {
    resolve,
    join,
    dirname,
    basename,
    extname,  
}
exposeInMainWorld('path', path)
// exposeInMainWorld('pathJoin', path.join)
// exposeInMainWorld('basename', path.basename)
// exposeInMainWorld('extname', path.extname)
// exposeInMainWorld('dirname', path.dirname)
