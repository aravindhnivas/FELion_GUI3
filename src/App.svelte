<script>
	import Navbar from "./components/Navbar.svelte"
	import Footer from "./components/Footer.svelte"
	import Home from "./Pages/Home.svelte"
	// import IconButton from "./testing/IconButton.svelte"
	import Layout from "./components/Layout.svelte"
	const navItems = ["Home", "Normline", "Masspec", "Timescan", "THz", "Powerfile", "Misc", "Settings"]

	// import {onMount} from "svelte"

	// onMount(()=>{document.getElementsByClassName("titlebar")[0].className += "animated fadeDown"})
</script>

<style>
	.pageContainer {
		max-height: 70vh;
		overflow-y: auto;
	}
</style>

<Navbar {navItems}/>

<Home />
<div class="pageContainer">
	{#each _.slice(navItems, 1) as id}
		<Layout {id} />
	{/each}
</div>
<!-- <IconButton /> -->
<Footer />