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
    'packages/main',
    'packages/preload',
    'packages/renderer/dist',
    
  ],
  extraFiles: [ // copy to ROOT_DIR (or Contents in mac)
    'CHANGELOG.md',
    'packages/renderer/dist/assets/python_files'
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

  win: {
    target: "nsis",
    asar: true
  },

  nsis: {
    oneClick: false
  }

};


module.exports = config;
