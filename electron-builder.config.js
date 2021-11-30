const now = new Date;
const buildVersion = `${now.getFullYear() - 2000}.${now.getMonth() + 1}.${now.getDate()}`;

/**
 * @type {import('electron-builder').Configuration}
 * @see https://www.electron.build/configuration/configuration
 */
const config = {

  directories: {
    output: 'dist',
    buildResources: 'buildResources',
  
  },
  files: [
    'packages/**/dist/**',
  ],
  
  
  extraMetadata: {
    version: buildVersion,
  },

  publish: [
    {
      provider: "github",
      owner: "aravindhnivas",
      repo: "FELion_GUI3"
    }
  ],

  // asarUnpack: [
  //   "./python3/",
  //   "./public/assets/python_files"
  // ],

  win: {
    target: "nsis",
    icon: "./public/assets/logo/win/icon.ico",
    asar: false
  },

  nsis: {
    oneClick: false
  }

};


module.exports = config;
