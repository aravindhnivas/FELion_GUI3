<script>
    import Configs from './misc/Configs.svelte'
    import EnergyConversion from './misc/EnergyConversion.svelte'
    import NumberDensity from './misc/NumberDensity.svelte'
    import Tab, { Label } from '@smui/tab'
    import TabBar from '@smui/tab-bar'
    import { onMount } from 'svelte'
    import { activePage } from '$src/svelteWritable'
    let active = window.db.get('MISC_active_tab') || 'Unit Conversion'
    $: if (active) {
        window.db.set('MISC_active_tab', active)
    }

    const navItems = ['Unit Conversion', 'Configs']
    let display = 'none'
    onMount(() => {
        display = $activePage === 'Misc' ? 'block' : 'none'
    })
</script>

<section class="animated fadeIn section" id="Misc" style:display>
    <div class="misc_main__div">
        <div class="box animated fadeInDown misc_nav">
            <TabBar tabs={navItems} let:tab bind:active>
                <Tab {tab}><Label>{tab}</Label></Tab>
            </TabBar>
        </div>

        <div class="misc_container">
            {#if active == 'Unit Conversion'}
                <div class="unit_conversion__container">
                    <EnergyConversion />
                    <NumberDensity />
                </div>
            {:else if active == 'Configs'}
                <Configs />
            {/if}
        </div>
    </div>
</section>

<style lang="scss">
    section {
        // overflow: hidden;
        padding: 2em;
        .misc_main__div {
            display: grid;
            gap: 1em;
            .unit_conversion__container {
                display: grid;
                grid-template-columns: 3fr 2fr;
                gap: 1em;
                // max-height: calc(100vh - 15rem);
            }
        }
    }
</style>
