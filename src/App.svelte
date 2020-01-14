<script>
	import Navbar from "./components/Navbar.svelte"
	import Footer from "./components/Footer.svelte"
	import IconButton from "./testing/IconButton.svelte"
	import Layout from "./Pages/Layout.svelte"
	const navItems = ["Home", "Normline", "Masspec", "Timescan", "THz", "Powerfile", "Misc", "Settings"]

</script>

<style>
	.pageContainer {
		max-height: 70vh;
		overflow-y: auto;
	}
</style>

<Navbar {navItems}/>

<div class="pageContainer">
	{#each navItems as id}
		<Layout {id} />
	{/each}
</div>
<IconButton />
<Footer />