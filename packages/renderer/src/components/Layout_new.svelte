<script lang="ts">
    import { graph_detached } from '$src/js/plot'
    import MainLayout from '$components/layouts/MainLayout.svelte'
    import ChromeTabs from '$components/layouts/ChromeTabs.svelte'
    export let id: string
    export let display = 'none'
    export let filetype = 'felix'

    const defaultAttribute = {
        fileChecked: [],
        currentLocation: '',
        fullfileslist: [],
        activateConfigModal: false,
        display: 'grid',
        id: '',
    }

    export let attributes: typeof defaultAttribute[] = [defaultAttribute]
    console.warn(attributes)
    setContext('filetype', filetype)
    const dispatch = createEventDispatcher()

    const default_location = (window.db.get(`${filetype}_location`) as string) || ''
    onMount(() => {
        console.log(id, 'mounted')
        $graph_detached[id] = false
    })
</script>

<section {id} style:display class="animate__animated animate__fadeIn">
    <div class="layout" style="overflow: hidden;">
        <ChromeTabs
            on:tabAdd={({ detail }) => {
                const id = detail.tabEl.id
                attributes = [
                    ...attributes.map((f) => ({ ...f, display: 'none' })),
                    {
                        ...defaultAttribute,
                        currentLocation: default_location,
                        id,
                        display: 'grid',
                    },
                ]
            }}
            on:tabRemove={({ detail }) => {
                const id = detail.tabEl.id
                attributes = attributes.filter((tab) => tab.id !== id)
            }}
            on:activeTabChange={({ detail }) => {
                const id = detail.tabEl.id
                dispatch('activeTabChange', { id })
                attributes = attributes.map((attribute) => {
                    if (attribute.id === id) {
                        return { ...attribute, display: 'grid' }
                    } else {
                        return { ...attribute, display: 'none' }
                    }
                })
            }}
        />
        {#each attributes as attribute, index (attribute.id)}
            {@const uniqueID = `-${attribute.id}`}
            {@const id = `${attribute.id}`}
            <svelte:component
                this={MainLayout}
                saveLocationToDB={index === 0}
                display={attribute.display}
                {uniqueID}
                on:configsaved
                {filetype}
                bind:fileChecked={attribute.fileChecked}
                bind:fullfileslist={attribute.fullfileslist}
                bind:currentLocation={attribute.currentLocation}
                bind:activateConfigModal={attribute.activateConfigModal}
            >
                <svelte:fragment slot="toggle_row">
                    <slot name="toggle_row" />
                </svelte:fragment>
                <svelte:fragment slot="buttonContainer">
                    <slot name="buttonContainer" {id} />
                </svelte:fragment>
                <svelte:fragment slot="plotContainer">
                    <slot name="plotContainer" {id} />
                </svelte:fragment>
                <svelte:fragment slot="plotContainer_functions">
                    <slot name="plotContainer_functions" />
                </svelte:fragment>
                <svelte:fragment slot="plotContainer_reports">
                    <slot name="plotContainer_reports" />
                </svelte:fragment>
                <svelte:fragment slot="config">
                    <slot name="config" />
                </svelte:fragment>
            </svelte:component>
        {/each}
    </div>
</section>

<style lang="scss">
    section {
        height: 100%;
    }
    .layout {
        height: 100%;
        display: grid;
        grid-template-rows: auto 1fr;
        overflow: hidden;
        gap: 0.5em;
    }
</style>
