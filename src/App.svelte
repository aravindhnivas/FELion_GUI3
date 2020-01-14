<script>
	import Navbar from "./components/Navbar.svelte"
	import Footer from "./components/Footer.svelte"
	import Layout from "./components/Layout.svelte"
	import Home from "./Pages/Home.svelte"
	const navItems = ["Home", "Normline", "Masspec", "Timescan", "THz", "Powerfile", "Misc", "Settings"]
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

	/* .pageContainer {
		max-height: 70vh;
		overflow-y: auto;
	} */
</style>

<Navbar {navItems}/>

<Home />
<div class="pageContainer">
	{#each _.slice(navItems, 1) as id}
		<Layout {id} />
	{/each}
</div>
<Footer />