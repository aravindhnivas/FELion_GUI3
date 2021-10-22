
const { contextBridge } = require('electron')
const {versions} = require("process")
require("./preload/fs-modules")
require("./preload/path-modules")
require("./preload/child-process-modules")
require("./preload/dialogs-modules")

require("./preload/jsondb-modules")
// require("./preload/extract-modules")
contextBridge.exposeInMainWorld("versions", versions)