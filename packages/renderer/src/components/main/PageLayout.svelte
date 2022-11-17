<script>
    import ChromeTabs from './ChromeTabs.svelte'

    export let component = null
    export let id = window.getID()
    // let component_id = window.getID()
    let tabs = []
    // $: console.log(tabs)
</script>

<main {id}>
    <!-- <ChromeTabs /> -->

    <ChromeTabs
        {id}
        on:tabAdd={({ detail }) => {
            const id = detail.tabEl.id
            tabs = [
                ...tabs.map((f) => ({ ...f, display: 'none' })),
                {
                    id,
                    display: 'grid',
                },
            ]
        }}
        on:tabRemove={({ detail }) => {
            const id = detail.tabEl.id
            tabs = tabs.filter((tab) => tab.id !== id)
        }}
        on:activeTabChange={({ detail }) => {
            const id = detail.tabEl.id
            tabs = tabs.map((tab) => {
                if (tab.id === id) {
                    return { ...tab, display: 'grid' }
                } else {
                    return { ...tab, display: 'none' }
                }
            })
        }}
    />

    {#each tabs as { id: tabID, display }, index (tabID)}
        {@const component_id = `page-${tabID}`}
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
