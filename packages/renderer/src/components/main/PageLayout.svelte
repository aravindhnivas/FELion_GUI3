<script>
    import DynamicTabs from '$src/components/DynamicTabs.svelte'

    export let component = null
    export let id = window.getID()
    let tabs = []
</script>

<main {id}>
    <DynamicTabs
        prefixId={id}
        on:tabAdd={({ detail: { id } }) => {
            // const id = detail.tabEl.id
            tabs = [
                ...tabs.map((f) => ({ ...f, display: 'none' })),
                {
                    id,
                    display: 'grid',
                },
            ]
        }}
        on:tabRemove={({ detail: { id } }) => {
            // const id = detail.tabEl.id
            tabs = tabs.filter((tab) => tab.id !== id)
        }}
        on:activeTabChange={({ detail: { id } }) => {
            // const id = detail.tabEl.id
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
