const customTitlebar = require('custom-electron-titlebar/lib/index');
let MyTitleBar = new customTitlebar.Titlebar({
    backgroundColor: customTitlebar.Color.fromHex('#38236b'),
    // icon: "./assets/images/icon.png"
});
MyTitleBar.updateTitle("FELion Spectrum Analyser");