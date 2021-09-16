
const { contextBridge } = require('electron')
const request = require('request');
const fs = require("fs");

contextBridge.exposeInMainWorld("request", (url, folder)=>{
    return new Promise((resolve, reject)=>{

        request
            .get(url)
            .on('response', function(response) {console.log("response: ", response)})
            .on('error', (error)=>reject(error))

            .pipe(fs.createWriteStream(folder))
            .on('close', ()=>{resolve("Download completed"); console.log("Done")})
    })
})