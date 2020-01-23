<script>

    import Radio from '@smui/radio'
    import FormField from '@smui/form-field'
    
    export let options = [], selected = "", style=""
</script>

{#each options as option}
    <FormField {style}>
        <Radio bind:group={selected} value={option}  />
        <span slot="label">{option}</span>
    
    </FormField>
{/each}