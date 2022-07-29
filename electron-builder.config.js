// const path = require('path')
// const certificate = path.join(__dirname, 'certificate') // path to the certificate
// const certificateFile = path.resolve(certificate, 'felion.pfx') // path to the private key

/**
 * @type {import('electron-builder').Configuration}
 * @see https://www.electron.build/configuration/configuration
 */
const config = {
    directories: {
        output: 'dist',
        buildResources: 'buildResources',
    },

    files: ['packages/**/dist/**'],
    extraFiles: [
        // copy to ROOT_DIR (or Contents in mac)
        'resources/*.md',
        'resources/python_files/**',
        'resources/felionpy/**',
    ],
    publish: [
        {
            provider: 'github',
            owner: 'aravindhnivas',
            repo: 'FELion_GUI3',
            releaseType: 'release',
        },
    ],
    win: {
        target: 'nsis',
        asar: true,
    },
    nsis: {
        oneClick: true,
    },
}
module.exports = config
