import svelte from 'rollup-plugin-svelte';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import livereload from 'rollup-plugin-livereload';
import { terser } from 'rollup-plugin-terser';
import autoPreprocess from 'svelte-preprocess';
import postcss from 'rollup-plugin-postcss';

import json from '@rollup/plugin-json';
import yaml from '@rollup/plugin-yaml';
import alias from '@rollup/plugin-alias';
import nodePolyfills from 'rollup-plugin-polyfill-node';

import path from "path";

const production = !process.env.ROLLUP_WATCH;
const PKG_DIR = path.resolve("./packages/")
const RENDERER_DIR = path.join(PKG_DIR, "renderer")


export default {

	input: path.join(RENDERER_DIR, "src/App.js"),
	output: [ { sourcemap: true, format: 'iife', name: 'app', file: path.join(RENDERER_DIR, 'public/build/bundle.js') } ],

	plugins: [
		nodePolyfills(),
		alias({
			entries: [
				{ find: '$src', replacement: path.join(RENDERER_DIR, "src") },
				{ find: '$public', replacement: path.join(RENDERER_DIR, 'public') },
				{ find: '$components', replacement: path.join(RENDERER_DIR, 'src/components') }
			]
		}),
		svelte({
			emitCss: true,
			compilerOptions: {dev: !production},
			preprocess: autoPreprocess()
		}),
		resolve({ browser:true, dedupe: ['svelte', 'svelte/transition', 'svelte/internal'] }),

		commonjs(),

		!production && livereload(path.join(RENDERER_DIR, 'public')),

		production && terser(),
		postcss({
			extract: 'bundle.css',

			minimize: true,
			sourceMap: true,
			use: [ ['sass', { includePaths: ['./node_modules'] }] ]
		}),
		json(), yaml()

	],
	watch: { clearScreen: false },

	external: ['electron', 'electron-updater']

};