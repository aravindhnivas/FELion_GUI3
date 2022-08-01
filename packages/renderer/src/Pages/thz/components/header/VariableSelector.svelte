<script lang="ts">
    import Textfield from '@smui/textfield'
    export let variable: string
    export let variableRange: VariableOptions
</script>

{#if variable !== 'time'}
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
