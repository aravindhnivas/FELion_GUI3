import { chrome } from '../../.electron-vendors.cache.json'
import { join } from 'path'
import { builtinModules } from 'module'

const PACKAGE_ROOT = __dirname

/**
 * @see https://vitejs.dev/config/
 */

const config = {
    mode: process.env.MODE,
    root: PACKAGE_ROOT,
    envDir: process.cwd(),
    resolve: {
        alias: {
            '/@/': join(PACKAGE_ROOT, 'src') + '/',
        },
    },
    build: {
        reportCompressedSize: false,
        sourcemap: process.env.MODE === 'development',
        target: `chrome${chrome}`,
        outDir: 'dist',
        assetsDir: '.',
        minify: process.env.MODE !== 'development',
        lib: {
            entry: 'preload.js',
            formats: ['cjs'],
        },
        rollupOptions: {
            external: [
                'electron',
                'electron-updater',
                'electron-unhandled',
                'electron-log',
                'fs-extra',
                ...builtinModules.flatMap((p) => [p, `node:${p}`]),
            ],
            output: {
                entryFileNames: '[name].cjs',
            },
        },
        emptyOutDir: true,
    },
}

export default config
