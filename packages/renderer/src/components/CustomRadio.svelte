<script>
    import Radio from '@smui/radio'
    import FormField from '@smui/form-field'

    export let options = []
    export let value = ''
    export let style = ''
</script>

{#each options as option}
    <FormField {style}>
        <Radio on:change bind:group={value} value={option} />
        <span slot="label">{option}</span>
    </FormField>
{/each}
