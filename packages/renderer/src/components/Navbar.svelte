<script lang="ts">
    import Tab, { Label } from '@smui/tab'
    import TabBar from '@smui/tab-bar'
    import { onMount } from 'svelte'
    import { activePage } from '$src/sveltewritables'

    export let navItems: string[] = []
    let active = <string>window.db.get('active_tab') || 'Home'
    $: $activePage = active
    $: console.log(`Current page: ${$activePage}`)
    $: window.db.set('active_tab', $activePage)

    const navigate = () => {
        navItems.forEach((item, i) => {
            item == active
                ? (document.getElementById(item).style.display = 'grid')
                : (document.getElementById(item).style.display = 'none')
        })
    }

    onMount(() => {
        document.getElementById('navbar').style.display = 'block'
        navigate()
    })
</script>

<div
    role="presentation"
    class="box animate__animated animate__fadeInDown"
    id="navbar"
    style="display:none; background: #5a419b;"
    on:click={navigate}
>
    <TabBar tabs={navItems} let:tab bind:active>
        <Tab {tab}><Label>{tab}</Label></Tab>
    </TabBar>
</div>

<style lang="scss">
    #navbar {
        width: 100vw;
        margin-bottom: 0;
        padding: 0;
    }
</style>
