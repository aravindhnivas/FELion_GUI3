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
    'resources'
  ],
  publish: [
    {
      provider: "github",
      owner: "aravindhnivas",
      repo: "FELion_GUI3",
      releaseType: "release"
    }
  ],
  win: {
    target: "nsis",
    asar: true
  },
  nsis: {
    oneClick: true
  }
};
module.exports = config;

