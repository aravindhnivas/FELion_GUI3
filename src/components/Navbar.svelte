<script>
	import Tab, {Icon, Label} from '@smui/tab';
	import TabBar from '@smui/tab-bar';
	import Button from '@smui/button';
	import {onMount} from "svelte"
	
	export let navItems;
	
	let active = 'Home';
	const navigate = () =>{navItems.forEach(item=> item == active ? showpage(item) : hidepage(item))}
	onMount(()=>{showpage("navbar"); showpage("Home")})
</script>

<section class="animated fadeInDown" id="navbar" style="display:none">
	<div on:click={navigate}>
		<TabBar tabs={navItems} let:tab bind:active>
			<Tab {tab}> <Label>{tab}</Label> </Tab>
		</TabBar>
	</div>
</section>


<style lang="scss">
  section > div {
    margin-bottom: 40px;
  }
  .icon-indicators :global(.mdc-tab-indicator--active .mdc-tab-indicator__content) {
    opacity: .2;
  }
</style>