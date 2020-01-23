<script>

	// Components
	import Navbar from "./components/Navbar.svelte"
	import Footer from "./components/Footer.svelte"
	import Layout from "./components/Layout.svelte"
	import LineAnimate from "./testing/LineAnimate.svelte"

	// Pages
	import Home from "./Pages/Home.svelte"
	import Powerfile from "./Pages/Powerfile.svelte"
	import Normline from "./Pages/Normline.svelte"
	import Masspec from "./Pages/Masspec.svelte"
	import Timescan from "./Pages/Timescan.svelte"
	import THz from "./Pages/THz.svelte"
	import Settings from "./Pages/Settings.svelte"

	
	import Modal from "./components/Modal.svelte"
	// import DialogChecklist from "./components/DialogChecklist.svelte"
	import {onMount, afterUpdate} from "svelte"

	onMount(()=>{
		let allbuttons = Array.from(document.querySelectorAll(".button"))
		allbuttons.forEach(button=>button.classList.add("hvr-glow"))
	})

	const navItems = ["Home", "Normline", "Masspec", "Timescan", "THz", "Powerfile", "Settings"]

	window.electron = require("electron")
	window.remote = electron.remote
	window.path = require("path")
	window.fs = require("fs")
	window.spawn = require("child_process").spawn
	
	export let version;

	console.log("Svelte: ", version)

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

<Navbar {navItems}/>

<Modal/>
<!-- <DialogChecklist /> -->
<Home />

<div class="pageContainer" style="overflow: hidden;">
	
	<Normline />
	<Masspec />
	<Timescan />
	<THz />
	<Powerfile />
	<Settings />

</div>

<Footer />