import App from './App.svelte';
import svelte from 'svelte/compiler';
import './App.scss';
import "./js/functions.js"
const app = new App({
	target: document.body,
	props: {
		version: svelte.VERSION
	}
});

export default app;