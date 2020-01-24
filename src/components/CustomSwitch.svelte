<script>

    import Switch from '@smui/switch'
    import FormField from '@smui/form-field'
    
    export let selected = false, style="", label=""
</script>

<FormField {style} on:change on:click>
    <Switch bind:checked={selected} />
    <span slot="label">{label}</span>
</FormField>