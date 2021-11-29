import App from './App.svelte';
import "./js/functions.js"
import 'cooltipz-css';
import 'ldbutton/dist/ldbtn.css';
// import './theme/smui.css';
import 'svelte-material-ui/bare.css';
import './theme/smui-theme-variables.scss';
import './App.scss';

const app = new App({target: document.body});
export default app;
