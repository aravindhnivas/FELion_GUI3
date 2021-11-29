
const { contextBridge } = require('electron')
const path = require("path")

contextBridge.exposeInMainWorld("pathResolve", function() {return path.resolve(...arguments)})
contextBridge.exposeInMainWorld("pathJoin", function() {return path.join(...arguments)})
contextBridge.exposeInMainWorld("basename", function(file) {return path.basename(file)})
contextBridge.exposeInMainWorld("extname", function(file) {return path.extname(file)})
contextBridge.exposeInMainWorld("dirname", function(file) {return path.dirname(file)})