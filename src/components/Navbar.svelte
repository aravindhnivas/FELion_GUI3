<script>
	import Tab, {Icon, Label} from '@smui/tab';
	import TabBar from '@smui/tab-bar';
	import Button from '@smui/button';
	import {onMount} from "svelte"
	
	export let navItems;
	
	let active = 'Home';
	const navigate = () =>{navItems.forEach(item=> item == active ? showpage(item) : hidepage(item))}
	onMount(()=>{showpage("navbar");})
</script>

<style lang="scss">
	#navbar { padding: 0.2em; width: 100vw; margin: 0; position: fixed;}
</style>

<div class="box animated fadeInDown" id="navbar" style="display:none" on:click={navigate}>
	<TabBar tabs={navItems} let:tab bind:active>
		<Tab {tab}> <Label>{tab}</Label> </Tab>
	</TabBar>
</div>
