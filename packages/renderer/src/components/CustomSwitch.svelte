<script>
    import Switch from '@smui/switch'
    import FormField from '@smui/form-field'
    export let selected = false
    export let style = ''
    export let label = ''
    export let tooltip = ''
    export let tooltipDir = 'bottom'
</script>

<FormField {style}>
    <Switch on:SMUISwitch:change bind:checked={selected} />
    <svelte:fragment slot="label">
        {#if tooltip}
            <span aria-label={tooltip} data-cooltipz-dir={tooltipDir}
                >{label}</span
            >
        {:else}
            <span>{label}</span>
        {/if}
    </svelte:fragment>
</FormField>
