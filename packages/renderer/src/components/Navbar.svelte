
<script>
	import Tab, {Label} from '@smui/tab';
	import TabBar       from '@smui/tab-bar';
	import {onMount}    from "svelte";
  	import {activePage} from '$src/sveltewritable';
	export let navItems;
	
	
	let active = db.get('active_tab') || 'Home';
	$: $activePage = active
	$: console.log(`Current page: ${$activePage}`)

	$: db.set('active_tab', $activePage)


	const navigate = () =>{navItems.forEach(
		item => item == active 
		? document.getElementById(item).style.display = "block" 
		: document.getElementById(item).style.display = "none" 
	)}
  
	onMount(()=>{document.getElementById("navbar").style.display = "block"; navigate()})
</script>

<div class="box animated fadeInDown" id="navbar" style="display:none" on:click={navigate}>
	<TabBar tabs={navItems} let:tab bind:active>
		<Tab {tab}> <Label>{tab}</Label> </Tab>
	</TabBar>
</div>


<style lang="scss">
	#navbar { width: 100vw; margin-bottom: 0; padding: 0; }
</style>