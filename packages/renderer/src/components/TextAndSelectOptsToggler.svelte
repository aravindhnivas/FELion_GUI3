<script>
    import Textfield from '@smui/textfield'
    import CustomSelect from './CustomSelect.svelte'
    export let value = ''
    export let label = ''
    // export let options = []
    // export let autoUpdate = false
    // export let update = () => {}

    export let toggle = true
    // console.log('toggle', toggle)

    // $: if(autoUpdate) {
    //     options.includes(value) ? options : value ? [value, ...options] : options
    // }
</script>

<svelte:component
    this={toggle ? CustomSelect : Textfield}
    on:click={(e) => {
        if (e.ctrlKey) toggle = !toggle
    }}
    on:change
    bind:value
    {label}
    {...$$restProps}
/>
