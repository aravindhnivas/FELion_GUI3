<script>
    import Textfield from '@smui/textfield'
    import CustomSelect from './CustomSelect.svelte'

    export let value = ''
    export let label = ''
    export let options = []
    export let update = () => {}

    let toggle = true
    console.log('toggle', toggle)
</script>

<svelte:component
    this={toggle ? CustomSelect : Textfield}
    on:click={(e) => {
        if (e.ctrlKey) toggle = !toggle
    }}
    bind:value
    {label}
    {update}
    options={options.includes(value) ? options : [value, ...options]}
/>
