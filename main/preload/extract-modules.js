
// const { contextBridge } = require('electron')
// const { extractFull } = require('node-7z-forall')

// contextBridge.exposeInMainWorld("extractFull", (zipfile, zipfolder, opts={})=>{
//     return new Promise((resolve, reject) => {
//         extractFull(zipfile, zipfolder, opts /* 7z options/switches */)
//             // .progress(function (files) {console.log('Some files are extracted: %s', files);})
//             .then(function () {resolve('Extracting done!');})
//             .catch(function (err) {reject(err);})
//     })
// })