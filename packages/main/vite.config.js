import { node } from '../../.electron-vendors.cache.json'
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
        sourcemap: 'inline',
        target: `node${node}`,
        outDir: 'dist',
        assetsDir: '.',
        minify: process.env.MODE !== 'development',
        lib: {
            entry: 'main.js',
            formats: ['cjs'],
        },
        rollupOptions: {
            external: [
                'electron',
                'electron-updater',
                ...builtinModules,
                // 'get-port'
            ],
            output: {
                entryFileNames: '[name].cjs',
            },
        },
        emptyOutDir: true,
        brotliSize: false,
    },
}

export default config
