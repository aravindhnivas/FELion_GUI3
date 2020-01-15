<script>

	// Components
	import Navbar from "./components/Navbar.svelte"
	import Footer from "./components/Footer.svelte"
	import Layout from "./components/Layout.svelte"
	import LineAnimate from "./testing/LineAnimate.svelte"

	// Pages
	import Home from "./Pages/Home.svelte"
	import Powerfile from "./Pages/Powerfile.svelte"
	
	const navItems = ["Home", "Normline", "Masspec", "Timescan", "THz", "Powerfile"]

	const pages = ["Normline", "Masspec", "Timescan", "THz"]
	import {onMount} from "svelte"

	window.electron = require("electron")
	window.remote = electron.remote
	window.path = require("path")
	window.fs = require("fs")

	onMount(()=>{
		// tippy("button") //Remember to initial tippy with target
	})

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

<style>
	.pageContainer {margin-top: 7em;}
</style>

<Navbar {navItems}/>
<LineAnimate />

<Home />

<div class="pageContainer">
	{#each pages as id}
		<Layout {id} />
	{/each}
	<Powerfile />
</div>


<Footer />