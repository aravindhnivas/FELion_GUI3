import { chrome } from '../../.electron-vendors.cache.json'
import { join } from 'path'
import { builtinModules } from 'module'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import autoPreprocess from 'svelte-preprocess'
// import Inspect from 'vite-plugin-inspect'
import AutoImport from 'unplugin-auto-import/vite'
const PACKAGE_ROOT = __dirname

const config = {
    mode: process.env.MODE,
    root: PACKAGE_ROOT,
    resolve: {
        alias: {
            $preload: join(PACKAGE_ROOT, '..', 'preload'),
            $src: join(PACKAGE_ROOT, 'src'),
            $components: join(PACKAGE_ROOT, 'src/components'),
            $computeCode: join(PACKAGE_ROOT, 'src/Pages/computeCode'),
        },
    },
    plugins: [
        svelte({ preprocess: autoPreprocess() }),
        // Inspect(),
        AutoImport({
            imports: ['svelte', 'svelte/store', 'svelte/transition'],
            dts: './src/auto-imports.d.ts',
        }),
    ],
    base: '',
    build: {
        reportCompressedSize: false,
        chunkSizeWarningLimit: 2000,
        sourcemap: true,
        target: `chrome${chrome}`,
        outDir: 'dist',
        assetsDir: '.',
        minify: process.env.MODE !== 'development',
        rollupOptions: {
            output: {
                manualChunks: {
                    winbox: ['winbox/src/js/winbox'],
                    interactjs: ['interactjs'],
                    yaml: ['yaml'],
                    'lodash-es': ['lodash-es'],
                    plotly: ['plotly.js-basic-dist'],
                },
            },
            external: [...builtinModules],
        },
        emptyOutDir: true,
    },
}
export default config
