<script lang="ts">
    import DynamicTabs from '$src/components/DynamicTabs.svelte'
    export let component = null
    export let id = window.getID()

    let tabs: { name: string; id: string; active: boolean }[] = []
</script>

<main {id}>
    <DynamicTabs bind:list={tabs} prefixId={id} />

    {#each tabs as { id: tabID, active }, index (tabID)}
        {@const component_id = `page-${tabID}`}
        {@const display = active ? 'grid' : 'none'}
        <svelte:component this={component} id={component_id} {display} saveLocationToDB={index === 0} />
    {/each}
</main>

<style>
    main {
        height: 100%;
        overflow: hidden;
        display: grid;
        grid-template-rows: auto 1fr;
    }
</style>
