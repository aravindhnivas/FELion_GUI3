<script context="module">
    export async function browse({
        filetype = '',
        dir = true,
        multiple = false,
    } = {}) {
        const type = dir ? 'openDirectory' : 'openFile'
        const options = {
            filters: [
                { name: filetype, extensions: [`*${filetype}`] },
                { name: 'All Files', extensions: ['*'] },
            ],
            properties: [type, multiple ? 'multiSelections' : ''],
        }

        const { showOpenDialogSync } = dialogs

        console.table(options)
        console.log('Directory: ', dir)
        console.log('multiSelections: ', multiple)

        const result = await showOpenDialogSync(options)
        const sendResult = dir ? result?.[0] : result
        console.log(sendResult)

        return sendResult
    }
</script>

<script>
    import { onMount, tick, createEventDispatcher } from 'svelte'
    import { fly, fade } from 'svelte/transition'
    import Textfield from '@smui/textfield'
    import { relayout } from 'plotly.js/dist/plotly-basic'
    import WinBox from 'winbox/src/js/winbox.js'
    import FileBrowser from '$components/FileBrowser.svelte'
    import Modal from '$components/Modal.svelte'
    import Editor from '$components/Editor.svelte'
    import { resizableDiv } from '$src/js/resizableDiv.js'
    ////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////

    export let id
    export let display = 'none'
    export let filetype = 'felix'
    export let fileChecked = []
    export let fullfileslist = []
    export let currentLocation = ''
    export let graphPlotted = false
    export let graphWindowClasses = ['no-full']
    export let activateConfigModal = false

    ////////////////////////////////////////////////////////////////////////////

    const dispatch = createEventDispatcher()
    async function browse_folder() {
        const result = await browse()
        if (!result) return
        currentLocation = result
        window.db.set(`${filetype}_location`, currentLocation)
        console.log(result, currentLocation)
    }

    onMount(() => {
        console.log(id, 'mounted')
        currentLocation = window.db.get(`${filetype}_location`) || ''
    })
    let graphDivContainer

    const lookForGraph = (node) => {
        try {
            graphDivs = Array.from(
                document.querySelectorAll(
                    `#${filetype}-plotContainer .graph__div`
                )
            )
        } catch (error) {
            console.log(error)
        }
    }

    function openGraph() {
        const graphWindow = new WinBox({
            class: graphWindowClasses,
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
        })
        graphWindow.maximize(true)
    }

    let graphDivs = []
    const changeGraphDivWidth = async (e) => {
        console.log('Updating graphDivs width')
        await tick()
        graphDivs.forEach((id) => {
            if (id.data) {
                relayout(id, { width: id.clientWidth })
            }
        })
    }
</script>

<section {id} style:display class="animated fadeIn">
    <div class="main__layout__div">
        <div
            use:resizableDiv
            on:resizeend={changeGraphDivWidth}
            style:touch-action="none"
            class="left_container__div box"
            transition:fly={{ x: -100, duration: 500 }}
        >
            <FileBrowser
                bind:currentLocation
                {filetype}
                bind:fileChecked
                on:chdir
                bind:fullfileslist
                on:markedFile
                on:fileselect
            />
        </div>

        <div
            class="right_container__div box "
            id="{filetype}__mainContainer__div"
        >
            <div class="location__div">
                <button
                    class="button is-link"
                    id="{filetype}_filebrowser_btn"
                    on:click={browse_folder}>Browse</button
                >

                <Textfield
                    bind:value={currentLocation}
                    label="Current location"
                    style="width:100%; "
                />
                <i
                    class="material-icons"
                    on:click={() => (activateConfigModal = true)}>build</i
                >
            </div>

            <div class="button__div align" id="{filetype}-buttonContainer">
                <slot name="buttonContainer" />

                {#if graphPlotted}
                    <button
                        class="button is-warning animated fadeIn"
                        on:click={openGraph}>Graph:Open separately</button
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
                <div
                    class="report-editor-div"
                    id="{filetype}-plotContainer-report-editor-div"
                >
                    <Editor
                        location={window.db.get(`${filetype}_location`)}
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
    .box {
        background-image: url(/assets/css/intro.svg);
        border-radius: 0;
        margin: 0;
    }
    .main__layout__div {
        display: grid;
        grid-auto-flow: column;
        width: 100%;

        height: calc(100vh - 6rem);
        grid-template-columns: auto 1fr;
        column-gap: 2em;

        .left_container__div {
            display: grid;
            grid-template-rows: auto auto auto 1fr;
            width: 100%;
        }

        .left_container__div,
        .right_container__div {
            max-height: calc(100vh - 6rem);
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
