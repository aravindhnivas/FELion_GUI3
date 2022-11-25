<script lang="ts">
    import { plot_colors } from '../../stores/common'
    import Textfield from '@smui/textfield'
    import CustomCheckbox from '$src/components/CustomCheckbox.svelte'
    import CustomSelect from '$src/components/CustomSelect.svelte'
    import MenuSurface from '@smui/menu-surface'
    import type { MenuSurfaceComponentDev } from '@smui/menu-surface'
    export let variable: string
    export let includeSUM: boolean = true
    export let variableRange: VariableOptions
    export let selected_stability_plots = []
    export let plots_to_include = { signal: true, main: true, boltzmann: false }

    const stability_plots_keys = ['coll', 'coll_rad', 'coll_att', 'coll_rad_att', 'coll_vs_rad', 'coll_vs_rad_att']
    $: console.log(selected_stability_plots)
    let stability_plot_surface: MenuSurfaceComponentDev
</script>

{#if variable == 'time'}
    <div class="align">
        <CustomCheckbox label="Relative population" bind:value={plots_to_include.main} />
        <CustomCheckbox label="Signal plot" bind:value={plots_to_include.signal} />
        <CustomCheckbox label="includeSUM" bind:value={includeSUM} />
        <Textfield class="ml-5" bind:value={$plot_colors} label="plots_colors (index)" />
        <div class="">
            <CustomCheckbox label="Boltzmann" bind:value={plots_to_include.boltzmann} />
            {#if plots_to_include.boltzmann}
                <button class="button is-link" on:click={() => stability_plot_surface?.setOpen(true)}
                    >select Boltzmann plots</button
                >
                <MenuSurface
                    style="background: var(--background-color);"
                    bind:this={stability_plot_surface}
                    anchorCorner="TOP_RIGHT"
                    anchorMargin={{ top: 0, right: 50, bottom: 0, left: 0 }}
                >
                    <div class="p-2" style="height: 250px; width: 250px;">
                        <CustomSelect
                            multiple={true}
                            bind:value={selected_stability_plots}
                            options={stability_plots_keys}
                            label="select plots"
                        />
                    </div>
                </MenuSurface>
            {/if}
        </div>
    </div>
{:else}
    <div class="variable__div">
        <Textfield
            class={variable === 'all' || variable === 'a(k_up/k_down)' ? '' : 'hide'}
            bind:value={$variableRange.k3_branch}
            label="a: (min, max, incremeant-step-size)"
        />
        <Textfield
            class={variable === 'all' || variable === 'Power(W)' ? '' : 'hide'}
            bind:value={$variableRange.power}
            label="P: (min, max, total-#steps-logarithmic-spaced)"
        />
        <Textfield
            class={variable === 'all' || variable === 'He density(cm-3)' ? '' : 'hide'}
            bind:value={$variableRange.numberDensity}
            label="nHe: (min, max, total-#steps-logarithmic-spaced)"
        />
        <Textfield
            class={variable === 'statistics' ? '' : 'hide'}
            bind:value={$variableRange.sampleSize}
            label="sample size"
        />
    </div>
{/if}

<style>
    .variable__div {
        display: grid;
        gap: 1em;
        width: 100%;
        grid-auto-flow: column;
    }
</style>
