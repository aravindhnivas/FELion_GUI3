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


const production = !process.env.ROLLUP_WATCH;

export default {

	input: 'src/App.js',


	output: [ { sourcemap: true, format: 'iife', name: 'app', file: 'static/bundle.js' } ],
	plugins: [
		nodePolyfills({
			exclude: ["admZip"]
		}),
		alias({
			entries: [
				{ find: 'src', replacement: './src' },
				{ find: 'components', replacement: './src/components' }
			]
		}),
		svelte({
			emitCss: true,
			compilerOptions: {dev: !production},
			preprocess: autoPreprocess()
		}),
		resolve({ browser:true, dedupe: ['svelte', 'svelte/transition', 'svelte/internal'] }),

		commonjs(),

		!production && livereload('static'),

		production && terser(),
		postcss({
			extract: 'bundle.css',

			minimize: true,
			sourceMap: true,
			use: [ ['sass', { includePaths: ['./src/theme', './node_modules'] }] ]
		}),
		json(), yaml()

	],
	watch: { clearScreen: false },
	external: ['electron']

};