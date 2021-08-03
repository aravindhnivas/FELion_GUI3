import svelte from 'rollup-plugin-svelte';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import livereload from 'rollup-plugin-livereload';
import { terser } from 'rollup-plugin-terser';
import autoPreprocess from 'svelte-preprocess';
import postcss from 'rollup-plugin-postcss';

import json from '@rollup/plugin-json';
import yaml from '@rollup/plugin-yaml';
import css from 'rollup-plugin-css-only';
const production = !process.env.ROLLUP_WATCH;

export default {
	input: 'src/App.js',

	output: [
		{ sourcemap: true, format: 'cjs', name: 'app', file: 'static/bundle.js' },
		// { sourcemap: true, format: 'cjs', name: 'app', file: 'static/bundle.min.js', plugins: [terser()] },

	],

	plugins: [
		svelte({
			emitCss: true,
			compilerOptions: {
				// enable run-time checks when not in production
				dev: !production
			},
			// we'll extract any component CSS out into
			// a separate file - better for performance
			preprocess: autoPreprocess()
		}),
		css({ output: 'bundle.css' }),
		resolve({ dedupe: ['svelte', 'svelte/transition', 'svelte/internal'] }),
		commonjs(),
		!production && livereload('static'),

		production && terser(),
		postcss({
			extract: true,
			minimize: true,

			
			sourceMap: true,
			use: [
				['sass', {
					includePaths: ['./src/theme', './node_modules']
				}]
			]
		}),

		json(), yaml()
	],

	watch: { clearScreen: false },
	external: ['electron', 'child_process', 'fs', 'path', 'url', 'module', 'os']
};