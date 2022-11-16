<script lang="ts">
    import { graph_detached } from '$src/js/plot'
    import MainLayout from '$components/layouts/MainLayout.svelte'
    import ChromeTabs from '$components/layouts/ChromeTabs.svelte'
    export let id: string
    export let display = 'none'
    export let filetype = 'felix'
    export let fileChecked: string[] = []
    export let fullfileslist: string[] = []
    export let currentLocation = ''
    export let graphPlotted = false
    export let activateConfigModal = false

    setContext('filetype', filetype)
    let tabsDisplay = 'none'
    onMount(() => {
        console.log(id, 'mounted')
        currentLocation = <string>window.db.get(`${filetype}_location`) || ''
        $graph_detached[id] = false
        tabsDisplay = 'grid'
    })
</script>

<section {id} style:display class="animate__animated animate__fadeIn">
    <div class="layout" style="overflow: hidden;">
        <ChromeTabs
            on:tabRemove={({ detail }) => {
                console.log(detail)
            }}
        />
        <MainLayout
            on:configsaved
            {filetype}
            bind:fileChecked
            bind:fullfileslist
            bind:currentLocation
            bind:graphPlotted
            bind:activateConfigModal
        >
            <svelte:fragment slot="toggle_row">
                <slot name="toggle_row" />
            </svelte:fragment>
            <svelte:fragment slot="buttonContainer">
                <slot name="buttonContainer" />
            </svelte:fragment>
            <svelte:fragment slot="plotContainer">
                <slot name="plotContainer" />
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
        </MainLayout>
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
