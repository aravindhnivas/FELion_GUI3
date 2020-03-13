import svelte from 'rollup-plugin-svelte';
import resolve from 'rollup-plugin-node-resolve';
import commonjs from 'rollup-plugin-commonjs';
import livereload from 'rollup-plugin-livereload';
import { terser } from 'rollup-plugin-terser';
import autoPreprocess from 'svelte-preprocess';
import postcss from 'rollup-plugin-postcss';

///////////////////////////////////////////////////////////////////////////


const production = !process.env.ROLLUP_WATCH;

export default {
	input: 'src/App.js',
	output: { sourcemap: true, format: 'cjs', name: 'app', file: 'static/bundle.js' },

	plugins: [
		svelte({
			emitCss: true,
			dev: !production,
			css: css => { css.write('static/bundle.css'); },
			preprocess: autoPreprocess()
		}),
		resolve({dedupe: ['svelte', 'svelte/transition', 'svelte/internal']}),
		commonjs(),
		!production && livereload('static'),

		production && terser(),
		postcss({
			extract: true,
			minimize: true,
			use: [
				['sass', {
					includePaths: ['./src/theme', './node_modules']
				}]
			]
		})
	],
	watch: { clearScreen: false },
	external: ['electron', 'child_process', 'fs', 'path', 'url', 'module', 'os']
};