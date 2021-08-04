
import 'source-map-support/register'
import App from './App.svelte';

import './App.scss';
import "./js/functions.js"
import "./js/modal.js"

const app = new App({
	
	target: document.body,
	props: { version: "" }
	
});
export default app;