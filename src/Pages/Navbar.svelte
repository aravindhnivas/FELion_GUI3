<script>
	import Tab, {Icon, Label} from '@smui/tab';
	import TabBar from '@smui/tab-bar';
	import Button from '@smui/button';
	import {onMount} from "svelte"
	export let navItems;
	let active = 'Home';
	window.showpage = (item) => document.getElementById(item).style.display = "block"
	window.hidepage = (item) => document.getElementById(item).style.display = "none"
	const navigate = () =>{navItems.forEach(item=> item == active ? showpage(item) : hidepage(item))}
	onMount(()=>showpage("Home"))
</script>

<section>
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