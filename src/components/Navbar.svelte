<script context="module">
  import {writable} from "svelte/store";
  export const activePage = writable("")

</script>
<script>
	import Tab, {Label} from '@smui/tab';
	import TabBar from '@smui/tab-bar';
	// import Button from '@smui/button';
	import {onMount} from "svelte";
	export let navItems;
	
	
	let active = 'Home';
	$: $activePage = active
	$: console.log(`Current page: ${$activePage}`)

	const navigate = () =>{navItems.forEach(item=> item == active ? showpage(item) : hidepage(item))}
	onMount(()=>{showpage("navbar");})
</script>

<style lang="scss">
	#navbar { width: 100vw; margin-bottom: 0; padding: 0; }
</style>


<div class="box animated fadeInDown" id="navbar" style="display:none" on:click={navigate}>
	<TabBar tabs={navItems} let:tab bind:active>
		<Tab {tab}> <Label>{tab}</Label> </Tab>
	</TabBar>
</div>
