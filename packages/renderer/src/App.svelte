
<script>
	import { windowLoaded } from './js/functions';
	import Navbar from "$components/Navbar.svelte"
	import Footer from "$components/Footer.svelte"
	import Home from "./Pages/Home.svelte"
	import Powerfile from "./Pages/Powerfile.svelte"
	import Normline from "./Pages/Normline.svelte"
	import Masspec from "./Pages/Masspec.svelte"
	import Timescan from "./Pages/Timescan.svelte"
	import THz from "./Pages/THz.svelte"
	import Settings from "./Pages/Settings.svelte"

	import Misc from "./Pages/Misc.svelte"
	import PreModal from "$components/PreModal.svelte";
	import {onMount, tick} from "svelte";
	import { SvelteToast } from '@zerodevx/svelte-toast'

	let mounted=false;



	onMount(async ()=>{
		const allbuttons = Array.from(document.querySelectorAll(".button"))
		allbuttons.forEach(button=>button.classList.add("hvr-glow"))
		await tick()
		mounted=true;
	})
	const navItems = ["Home", "Normline", "Masspec", "Timescan", "THz", "Powerfile", "Misc", "Settings"]
</script>

{#if $windowLoaded}
	{#if mounted}
		<PreModal />
		<SvelteToast />

	{/if}

	<Navbar {navItems} />
	<Home />
	<div id="pageContainer" style="overflow: hidden;display: {mounted ? 'block': 'none'}">
		<Normline />
		<Masspec />
		<Timescan />
		<THz />
		<Powerfile />
		<Misc />
		<Settings />
	</div>
	<Footer />
{/if}

<!-- <style global lang="scss">
	// css
	@import 'cooltipz-css';
	@import 'ldbutton/dist/ldbtn.css';
	@import 'svelte-material-ui/bare.css';

	// scss
	@import './scss/smui-theme-variables.scss';
	@import "./scss/materialTheme.scss";
	@import "./scss/bulma-style.scss";
	@import "./scss/styles.scss";
</style> -->