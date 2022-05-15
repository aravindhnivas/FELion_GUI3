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

<section
    class="animate__animated animate__fadeIn section"
    id="Misc"
    style:display
>
    <div class="misc_main__div">
        <div class="box animate__animated animate__fadeInDown misc_nav">
            <TabBar tabs={navItems} let:tab bind:active>
                <Tab {tab}><Label>{tab}</Label></Tab>
            </TabBar>
        </div>

        <div class="misc_container">
            <!-- {#if active == 'Unit Conversion'} -->
            <div
                class="unit_conversion__container"
                style:display={active == 'Unit Conversion' ? 'grid' : 'none'}
            >
                <EnergyConversion />
                <NumberDensity />
            </div>
            <!-- {:else if active == 'Configs'} -->
            <Configs {active} />
            <!-- {/if} -->
        </div>
    </div>
</section>

<style lang="scss">
    section {
        padding: 1em;

        height: calc(100vh - 7rem);
        .misc_main__div {
            display: grid;
            gap: 1em;
            height: 100%;
            grid-template-rows: auto 1fr;
            .misc_container {
                height: 100%;
            }

            .misc_nav {
                padding: 0;
            }
            .unit_conversion__container {
                display: grid;
                gap: 1em;
                grid-template-columns: 3fr 2fr;

                // max-height: calc(100vh - 15rem);
            }
        }
    }
</style>
