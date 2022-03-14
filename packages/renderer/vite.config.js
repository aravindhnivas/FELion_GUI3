/* eslint-env node */

import {chrome} from '../../.electron-vendors.cache.json';
import {join} from 'path';
import { builtinModules } from 'module';
import { svelte } from '@sveltejs/vite-plugin-svelte'
import autoPreprocess from 'svelte-preprocess';


const PACKAGE_ROOT = __dirname;



const config = {
  mode: process.env.MODE,
  root: PACKAGE_ROOT,
  // emptyOutDir: true,
  resolve: {
    alias: {
      '$preload': join(PACKAGE_ROOT, '..', 'preload'),
      '$src': join(PACKAGE_ROOT, 'src'),
      '$components': join(PACKAGE_ROOT, 'src/components'),
      '$computeCode': join(PACKAGE_ROOT, 'src/Pages/computeCode'),
    },
  },
  plugins: [svelte({preprocess: autoPreprocess()})],
  base: '',
  build: {
    reportCompressedSize: false,
    chunkSizeWarningLimit: 2000,
    sourcemap: true,
    target: `chrome${chrome}`,
    outDir: 'dist',
    assetsDir: '.',
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
    brotliSize: false
  },

};
export default config;

