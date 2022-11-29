<script lang="ts">
    import { activePage } from '$src/sveltewritables'
    import Tab, { Label } from '@smui/tab'
    import TabBar from '@smui/tab-bar'
    import { onMount } from 'svelte'
    import Badge from '@smui-extra/badge'

    export let navItems: string[] = []

    const navigate = () => {
        navItems.forEach((item) => {
            item === $activePage
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
    <TabBar tabs={navItems} let:tab bind:active={$activePage}>
        <Tab {tab}>
            <Label>
                <span class="mr-3">{tab}</span>
                <Badge
                    class="navbar-badge"
                    aria-label="{tab}-navbar-status-badge"
                    id="navbar-badge-{tab}"
                    style="min-height: 10px; min-width: 10px; padding: 0; background: '';"
                />
            </Label>
        </Tab>
    </TabBar>
</div>

<style lang="scss" global>
    #navbar {
        width: 100vw;
        margin-bottom: 0;
        padding: 0;
        .navbar-badge {
            top: 15px;
        }
    }
</style>
