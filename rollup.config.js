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
const production = !process.env.ROLLUP_WATCH;

export default {
	input: 'src/App.js',
	output: [ { sourcemap: true, format: 'cjs', name: 'app', file: 'static/bundle.js' } ],

	plugins: [


		alias({
			entries: [
				{ find: 'src', replacement: './src' },
				{ find: 'components', replacement: './src/components' }
			]
		}),


		svelte({
			emitCss: false,
			compilerOptions: {
				dev: !production,
				css: css => { css.write('bundle.css'); },
			},
		
			preprocess: autoPreprocess()
		}),
		resolve({ dedupe: ['svelte', 'svelte/transition', 'svelte/internal'] }),
		commonjs(),
		!production && livereload('static'),
		production && terser(),
		postcss({
			extract: true,
			minimize: true,

			sourceMap: true,

			use: [ ['sass', { includePaths: ['./src/theme', './node_modules'] }] ]
		}),
		json(), yaml()

	
	],
	
	watch: { clearScreen: false },
	external: ['electron', 'child_process', 'fs', 'path', 'url', 'module', 'os']

};