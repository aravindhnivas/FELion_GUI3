<script context="module">
    import { writable } from 'svelte/store'
    import { components } from '$src/Pages/configs/Components.svelte'
    import configs_json from './configs.json'
    export const configs = writable(configs_json)
</script>

{#each Object.keys($configs) as key (key)}
    {@const component = components[$configs[key].component]}
    <svelte:component this={component} label={key} bind:value={$configs[key].value} />
{/each}
