<script lang="ts" context="module">
    import type { OpenDialogSyncOptions } from 'electron'

    export async function browse({ filetype = '', dir = true, multiple = false } = {}) {
        const properties = []
        const type = dir ? 'openDirectory' : 'openFile'

        properties.push(type)

        if (multiple) {
            properties.push('multiSelections')
        }

        const options: OpenDialogSyncOptions = {
            filters: [
                { name: filetype, extensions: [`*${filetype}`] },
                { name: 'All Files', extensions: ['*'] },
            ],
            properties,
        }

        const { showOpenDialogSync } = window.dialogs

        console.table(options)
        console.log('Directory: ', dir)
        console.log('multiSelections: ', multiple)

        const result = (await showOpenDialogSync(options)) || ['']
        return result
    }

    export const graph_detached: { [name: string]: boolean } = {}
</script>

<script lang="ts">
    import { onMount, createEventDispatcher, tick, onDestroy } from 'svelte'
    import { fly, fade } from 'svelte/transition'
    import Textfield from '@smui/textfield'
    import { relayout } from 'plotly.js/dist/plotly-basic'
    import WinBox from 'winbox/src/js/winbox.js'
    import FileBrowser from '$components/FileBrowser.svelte'
    import Modal from '$components/Modal.svelte'
    import Editor from '$components/Editor.svelte'
    import { resizableDiv } from '$src/js/resizableDiv.js'

    export let id: string
    export let display = 'none'
    export let filetype = 'felix'
    export let fileChecked = []
    export let fullfileslist = []
    export let currentLocation = ''
    export let graphPlotted = false
    export let activateConfigModal = false

    const dispatch = createEventDispatcher()
    async function browse_folder() {
        const [result] = await browse()
        if (!result) return
        currentLocation = result
        window.db.set(`${filetype}_location`, currentLocation)
    }

    onMount(() => {
        graphPlotted = false
        console.log(id, 'mounted')
        currentLocation = <string>window.db.get(`${filetype}_location`) || ''
        graph_detached[id] = false
    })

    let graphDivContainer
    let graphDivs = []

    const lookForGraph = (node) => {
        try {
            graphDivs = Array.from(document.querySelectorAll(`#${filetype}-plotContainer .graph__div`))
        } catch (error) {
            console.log(error)
        }
    }

    let graphWindow
    let graphwindowClosed = false

    function openGraph() {
        graphwindowClosed = false
        graphWindow = new WinBox({
            class: ['no-full'],
            root: document.getElementById('pageContainer'),
            mount: graphDivContainer,
            title: `Modal: ${filetype}`,
            x: 'center',
            y: 'center',
            width: '70%',
            height: '70%',
            background: '#634e96',
            top: 50,
            bottom: 50,
            onclose: () => {
                graphwindowClosed = true
                graph_detached[id] = false
            },
        })

        graphWindow?.maximize(true)
        changeGraphDivWidth()

        graph_detached[id] = true
    }

    $: if (graphwindowClosed) {
        changeGraphDivWidth()
    }

    const changeGraphDivWidth = async (event?: CustomEvent) => {
        await tick()
        graphDivs?.forEach((id) => {
            if (!id?.data) return
            try {
                relayout(id, { width: id.clientWidth })
            } catch (error) {
                console.log('could not relayout', error)
            }
        })
    }

    onDestroy(() => {
        graphWindow?.close()
        console.log(id, 'destroyed')
    })
    let location = (window.db.get(`${filetype}_location`) as string) || ''
    $: console.log({ graphPlotted })
</script>

<section {id} style:display class="animate__animated animate__fadeIn">
    <div class="main__layout__div">
        <div
            use:resizableDiv
            on:resizeend={changeGraphDivWidth}
            style:touch-action="none"
            class="left_container__div box background-body"
            transition:fly={{ x: -100, duration: 500 }}
        >
            <FileBrowser
                on:markedFile
                on:fileselect
                bind:currentLocation
                {filetype}
                bind:fileChecked
                on:chdir
                bind:fullfileslist
            />
        </div>

        <div class="right_container__div box background-body " id="{filetype}__mainContainer__div">
            <div class="location__div">
                <button class="button is-link" id="{filetype}_filebrowser_btn" on:click={browse_folder}>Browse</button>
                <Textfield bind:value={currentLocation} label="Current location" style="width:100%; " />
                <i class="material-icons" on:click={() => (activateConfigModal = true)}>build</i>
            </div>

            <div class="button__div align" id="{filetype}-buttonContainer">
                <slot name="buttonContainer" />
                {#if graphPlotted}
                    <button class="button is-warning animate__animated animate__fadeIn" on:click={openGraph}
                        >Graph:Open separately</button
                    >
                {/if}
            </div>
            <div
                class="plot__div"
                id="{filetype}-plotContainer"
                transition:fade
                use:lookForGraph
                bind:this={graphDivContainer}
            >
                <slot name="plotContainer" {lookForGraph} />
                {#if graphPlotted}
                    <slot name="plotContainer_functions" />
                    <slot name="plotContainer_reports" />
                {/if}
                <div class="report-editor-div" id="{filetype}-plotContainer-report-editor-div">
                    <Editor
                        {location}
                        {filetype}
                        id="{filetype}-report-editor"
                        mount="#{filetype}-plotContainer-report-editor-div"
                    />
                </div>
            </div>
        </div>

        {#if activateConfigModal}
            <Modal
                on:close={() => console.log('modal closed')}
                title="{filetype.toUpperCase()} Settings"
                bind:active={activateConfigModal}
            >
                <svelte:fragment slot="content">
                    <slot name="config" />
                </svelte:fragment>

                <svelte:fragment slot="footerbtn">
                    <button
                        class="button is-link"
                        on:click={() => {
                            dispatch('configsaved', { filetype })
                        }}>Save</button
                    >
                </svelte:fragment>
            </Modal>
        {/if}
    </div>
</section>

<style lang="scss">
    section {
        height: 100%;
    }
    .box {
        // background-image: url(/assets/css/intro.svg);
        border-radius: 0;
        margin: 0;
    }
    .main__layout__div {
        display: grid;
        grid-auto-flow: column;
        width: 100%;

        height: 100%;
        grid-template-columns: auto 1fr;
        column-gap: 2em;

        .left_container__div {
            display: grid;
            grid-template-rows: auto 1fr;
            width: 100%;
            min-width: 300px;
        }

        .left_container__div,
        .right_container__div {
            overflow: hidden;
            // max-height: calc(100vh - 6rem);
            // height: 100%;
        }

        .right_container__div {
            display: grid;
            row-gap: 1em;
            grid-template-rows: auto auto 1fr;
            .location__div {
                display: grid;
                grid-template-columns: auto 1fr auto;
                column-gap: 1em;
                align-items: baseline;
            }
        }
    }
    .plot__div {
        display: flex;
        row-gap: 1em;
        flex-direction: column;
        overflow: auto;
        padding-right: 1em;
        padding-bottom: 12em;
    }
</style>
