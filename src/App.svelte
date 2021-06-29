
<script>

	import { mainPreModal } from './svelteWritable';
	import Navbar from "./components/Navbar.svelte"
	import Footer from "./components/Footer.svelte"
	import Home from "./Pages/Home.svelte"
	import Powerfile from "./Pages/Powerfile.svelte"
	
	import Normline from "./Pages/Normline.svelte"
	import Masspec from "./Pages/Masspec.svelte"
	import Timescan from "./Pages/Timescan.svelte"
	
	import THz from "./Pages/THz.svelte"
	
	
	import Settings from "./Pages/Settings.svelte"
	import Misc from "./Pages/Misc.svelte"
	import PreModal from "./components/PreModal.svelte";
	import {onMount, tick} from "svelte";


	let mounted=false;

	onMount(async ()=>{
		let allbuttons = Array.from(document.querySelectorAll(".button"))
		allbuttons.forEach(button=>button.classList.add("hvr-glow"))
		await tick()
		mounted=true;
	})

	const navItems = ["Home", "Normline", "Masspec", "Timescan", "THz", "Powerfile", "Misc", "Settings"]
	

	window.Menu = remote.Menu
	window.MenuItem = remote.MenuItem

	let menu = new Menu()
	let rightClickPosition;

	menu.append(new MenuItem({ label: 'Reload', role:"reload" }))

	menu.append(new MenuItem({ label: 'DevTools', role: 'toggledevtools' }))

	menu.append(new MenuItem({ label: "Inspect Element", click() { remote.getCurrentWindow().inspectElement(rightClickPosition.x, rightClickPosition.y) } }))

	window.addEventListener('contextmenu', (e) => {
      e.preventDefault()
      rightClickPosition = {x: e.x, y: e.y}


      menu.popup(remote.getCurrentWindow())
  }, false)
</script>

{#if mounted}
	<PreModal bind:preModal={$mainPreModal} />
{/if}

<Navbar {navItems}/>
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