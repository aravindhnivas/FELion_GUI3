

const Plotly =  require("./assets/js/plotly-latest.min.js");
require("./assets/js/winbox.bundle.js");

window._ = require('./assets/js/lodash.js')
window.electron = require("electron")
window.remote = electron.remote
window.path = require("path")
window.fs = require("fs")
window.spawn = require("child_process").spawn
const JSONdb = require('./assets/js/JSONdb')

const db = new JSONdb(path.resolve(__dirname, "db.json"))
const versionFile_ = path.resolve(__dirname, "../version.json")
const versionFileContent = fs.readFileSync(versionFile_).toString("utf-8")
const versionFileJSON = JSON.parse(versionFileContent)

window.currentVersion = versionFileJSON.version
db.set("version", currentVersion)