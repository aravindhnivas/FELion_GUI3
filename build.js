var electronInstaller = require('electron-winstaller');
var settings = {
    appDirectory: '../github_project/release-builds/FELion_GUI3-win32-x64',
    outputDirectory: '../github_project/release-builds/installer',
    authors: 'Aravindh', loadingGif:"./loading.gif",
    exe: 'FELion_GUI3.exe', setupExe: "FELion_GUI3.exe",
    description: 'FELion Spectrum Analyser'
    
};
resultPromise = electronInstaller.createWindowsInstaller(settings);
resultPromise.then(() => { console.log("Installer created");
}, (e) => {console.log(`Error Occured: ${e.message}`)});