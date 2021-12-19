/* eslint-env node */

import {chrome} from '../../electron-vendors.config.json';
import {join} from 'path';
import { builtinModules } from 'module';
import {defineConfig} from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte'
import {loadAndSetEnv} from '../../scripts/loadAndSetEnv.mjs';
import autoPreprocess from 'svelte-preprocess';

const PACKAGE_ROOT = __dirname;

/**
 * Vite looks for `.env.[mode]` files only in `PACKAGE_ROOT` directory.
 * Therefore, you must manually load and set the environment variables from the root directory above
 */
loadAndSetEnv(process.env.MODE, process.cwd());

export default defineConfig({
  root: PACKAGE_ROOT,
  resolve: {
    alias: {
      '$src': join(PACKAGE_ROOT, 'src'),
      '$components': join(PACKAGE_ROOT, 'src/components'),
      '$computeCode': join(PACKAGE_ROOT, 'src/Pages/computeCode'),
    },
  },
  plugins: [svelte({preprocess: autoPreprocess()})],
  base: '',
  server: {
    fsServe: {
      root: join(PACKAGE_ROOT, '../../'),
    },
  },
  build: {
    reportCompressedSize: false,
    chunkSizeWarningLimit: 2000,
    sourcemap: true,
    target: `chrome${chrome}`,
    outDir: 'dist',
    assetsDir: '.',
    terserOptions: {
      ecma: 2020,
      compress: {
        passes: 2,
      },
      safari10: false,
    },
    rollupOptions: {
      output: {
        manualChunks: {
          winbox: ['winbox/src/js/winbox'],
          interactjs: ['interactjs'],
          yaml: ['yaml'],
          remarkable: ['remarkable'],
          'lodash-es': ['lodash-es'],
          'plotly': ['plotly.js/dist/plotly-basic'],
        }
      },
      external: [
        ...builtinModules, "electron-updater", "electron-log"
      ],
    },
    emptyOutDir: true,
  },
});

