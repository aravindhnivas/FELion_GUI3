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