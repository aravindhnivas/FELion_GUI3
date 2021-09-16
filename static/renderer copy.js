
import "./static/assets/js/winbox.bundle.js"
import Plotly from "./static/assets/js/plotly-latest.min.js-latest.min.js"
import JSONdb from"./static/assets/js/JSONdbatic/assets/js/JSONdb"
import lodash from'./static/assets/js/lodash.js'
import path from "path"
import fs from "fs"
import { spawn, exec } from "child_process"
import https from 'https'
import admZip from 'adm-zip'



window.Plotly =  Plotly
window._ = lodash
window.path = path
window.fs = fs
window.spawn = spawn
window.exec = exec
window.admZip = admZip
window.https = https
window.JSONdb = JSONdb
window.db = new JSONdb(path.resolve(__dirname, "db.json"))
window.versionFile_ = path.resolve(__dirname, "../version.json")
window.versionFileContent = fs.readFileSync(versionFile_).toString("utf-8")
window.versionFileJSON = JSON.parse(versionFileContent)
window.currentVersion = versionFileJSON.version
db.set("version", currentVersion)