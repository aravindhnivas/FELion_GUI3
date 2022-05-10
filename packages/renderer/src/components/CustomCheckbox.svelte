<script lang="ts">
    import Checkbox from '@smui/checkbox'
    import FormField from '@smui/form-field'

    export let value: boolean = false
    export let label: string = 'Check me'
    export let style: string = ''
</script>

<FormField {style}>
    <Checkbox bind:checked={value} />
    <span slot="label">{label}</span>
</FormField>
