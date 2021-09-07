const customTitlebar = require('./custom-electron-titlebar/lib/index')
const MyTitleBar = new customTitlebar.Titlebar({ 
    backgroundColor: customTitlebar.Color.fromHex('#38236b'),
    menu: null, icon: "./assets/logo/felion_icon.svg"
});

MyTitleBar.updateTitle("FELion Spectrum Analyser")