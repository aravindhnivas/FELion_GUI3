<script>

    import Radio from '@smui/radio'
    import FormField from '@smui/form-field'
    
    export let options = [], selected = ""
</script>

{#each options as option}
    <FormField >
        <Radio bind:group={selected} value={option}  />
        <span slot="label">{option}</span>
    
    </FormField>
{/each}