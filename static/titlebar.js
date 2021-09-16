import customTitlebar from "./custom-electron-titlebar/lib/index.js";
const MyTitleBar = new customTitlebar.Titlebar({ 
    backgroundColor: customTitlebar.Color.fromHex('#38236b'),
    menu: null, icon: "./assets/logo/felion_icon.svg"
});

MyTitleBar.updateTitle("FELion Spectrum Analyser")