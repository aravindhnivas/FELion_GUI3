<script lang="ts">
    import { plot_colors } from '../../stores/common'
    import Textfield from '@smui/textfield'
    import CustomCheckbox from '$src/components/CustomCheckbox.svelte'

    export let variable: string
    export let variableRange: VariableOptions
    export let plots_to_include = { signal: true, main: true, population_stability: false }
</script>

{#if variable == 'time'}
    <div class="align">
        <CustomCheckbox label="Population ratio simulation plot" bind:value={plots_to_include.main} />
        <CustomCheckbox label="Signal plot" bind:value={plots_to_include.signal} />
        <CustomCheckbox label="population stability plot" bind:value={plots_to_include.population_stability} />
        <Textfield bind:value={$plot_colors} label="plots_colors (index)" />
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
