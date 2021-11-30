<script>

    import Switch from '@smui/switch'
    import FormField from '@smui/form-field'
    
    export let selected = false, style="", label=""
</script>

<FormField {style}>
    <Switch on:SMUISwitch:change bind:checked={selected} />
    <span slot="label">{label}</span>
</FormField>