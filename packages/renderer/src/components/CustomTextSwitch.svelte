<script>
    import Textfield from '@smui/textfield'

    export let min = 0
    export let value = ''
    export let label = ''
    export let style = ''
    export let step = 1
    export let variant = 'standard'

    let changeStepsize = false
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
        input$step={step}
        input$type="number"
    />
{/if}
