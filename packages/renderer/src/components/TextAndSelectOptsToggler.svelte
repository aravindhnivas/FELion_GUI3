<script>
    import Textfield from '@smui/textfield'
    import CustomSelect from './CustomSelect.svelte'
    export let value = ''
    export let label = ''
    export let toggle = true
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
