import svelte from 'rollup-plugin-svelte';
import resolve from 'rollup-plugin-node-resolve';
import commonjs from 'rollup-plugin-commonjs';
import livereload from 'rollup-plugin-livereload';
import { terser } from 'rollup-plugin-terser';
import sass from 'node-sass';
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
			preprocess: {
				style: async ({ content, attributes }) => {
					if (attributes.type !== 'text/scss' && attributes.lang !== 'scss') return;

					return new Promise((resolve, reject) => {
						sass.render({
							data: content,
							includePaths: ['src'],
							sourceMap: false,
							outFile: 'x' // this is necessary, but is ignored
						}, (err, result) => {
							if (err) return reject(err);

							resolve({
								code: result.css.toString(),
								map: result.map ? result.map.toString() : ""
							});
						});
					});
				}
			}
		}),

		
		resolve({ }),
		commonjs(),
		!production && livereload('static'),

		production && terser(),

		postcss({
			extract: true,

			minimize: true,
			use: [
				['sass', {
				includePaths: [ './src/theme', './node_modules' ]
				}]
			]
		})
	],

	watch: { clearScreen: false },
	external: [ 'electron', 'child_process', 'fs', 'path', 'url', 'module', 'os']
};