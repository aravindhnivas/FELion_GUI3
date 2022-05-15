<script>
    import Switch from '@smui/switch'
    import FormField from '@smui/form-field'
    import { createEventDispatcher } from 'svelte'

    export let selected = false
    export let style = ''
    export let label = ''
    export let tooltip = ''
    export let tooltip_direction = 'bottom'
    const dispatch = createEventDispatcher()
</script>

<FormField {style}>
    <Switch
        on:SMUISwitch:change={(e) => dispatch('change', { event: e, selected })}
        bind:checked={selected}
    />
    <svelte:fragment slot="label">
        {#if tooltip}
            <span aria-label={tooltip} data-cooltipz-dir={tooltip_direction}
                >{label}</span
            >
        {:else}
            <span>{label}</span>
        {/if}
    </svelte:fragment>
</FormField>
