<script lang="ts">
    import Textfield from '@smui/textfield'

    export let min: number | string = 0
    export let max: number | string = null
    export let value: number | string = ''
    export let label: string = ''
    export let style: string = ''
    export let step: number | string = 1
    export let variant: string = 'standard'

    let changeStepsize: boolean = false
</script>

{#if changeStepsize}
    <Textfield
        bind:value={step}
        {style}
        {variant}
        label="enter stepSize"
        on:keyup={({ key }) => {
            if (key == 'Enter') {
                changeStepsize = false
            }
        }}
        on:click={({ shiftKey }) => {
            if (shiftKey) {
                changeStepsize = false
            }
        }}
    />
{:else}
    <Textfield
        bind:value
        {style}
        {variant}
        {label}
        on:keyup
        on:change
        on:click={({ shiftKey }) => {
            if (shiftKey) {
                changeStepsize = true
            }
        }}
        input$min={min}
        input$max={max}
        input$step={step}
        type="number"
    />
{/if}
