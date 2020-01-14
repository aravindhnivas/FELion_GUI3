<script>
	import Navbar from "./Pages/Navbar.svelte"
	import Layout from "./Pages/Layout.svelte"
	import Table from "./components/Tables.svelte"
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
<!-- <Table /> -->