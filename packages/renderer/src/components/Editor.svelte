<script>
    import { onDestroy } from 'svelte'
    import Textfield from '@smui/textfield'
    import { browse } from '$components/Layout.svelte'
    import CustomDialog from '$components/CustomDialog.svelte'
    import WinBox from 'winbox/src/js/winbox.js'
    import CustomSwitch from '$components/CustomSwitch.svelte'

    export let id = getID()
    export let location = ''
    export let filetype = ''
    export let editor=null;

    export let mount = null
    export let mainTitle = 'Report/Editor'
    export let reportRead = false
    export let savefilename = 'report'
    export let reportSaved = false
    export let showReport = false
    export let enable_location_browser = true

    async function mountEditor(node) {
        try {
            editor = await ClassicEditor.create(node, {
                toolbar: { shouldNotGroupWhenFull: true },
            })
            readFromFile(false)
        } catch (error) {
            window.handleError(error)
        }
    }

    onDestroy(() => {
        if (editor) {
            editor.destroy()
            console.info('editor destroyed')
        }
    })

    $: if (!showReport && editor) {
        editor.destroy()
        console.info('editor destroyed')
    }
    if (window.db.get(`${filetype}-report-md`)) {
        location = window.db.get(`${filetype}-report-md`)
    }

    $: reportFile = window.pathJoin(
        location,
        savefilename.endsWith('.md') ? savefilename : `${savefilename}.md`
    )
    let reportFiles = []

    const updateFiles = (node = null) => {
        node?.target?.classList.add('rotateIn')
        reportFiles = fs
            .readdirSync(pathResolve(location))
            .filter((name) => name.endsWith('.md'))
            .map((name) => name.replace(extname(name), ''))
    }

    $: if (fs.existsSync(location)) {
        window.db.set(`${filetype}-report-md`, location)
        updateFiles()
    }

    async function browse_folder() {
        const result = await browse()
        if (!result) return
        location = result
        window.createToast('Location updated')
    }

    const saveReport = ({ overwrite = false }) => {
        try {
            if (!location)
                return window.createToast('UNDEFINED location', 'danger')
            if (fs.existsSync(reportFile) && !overwrite) {
                overwriteDialogOpen = true
                return
            }
            fs.writeFileSync(reportFile, editor.getData())

            reportSaved = true
            window.createToast(`${basename(reportFile)} file saved`, 'success')
        } catch (error) {
            window.handleError(error)
        }
    }

    let reportWindowClosed = true

    function openReport() {
        const graphWindow = new WinBox({
            root: document.getElementById('pageContainer'),
            mount: document.querySelector(mount),
            title: `Report ${filetype} `,
            x: 'center',
            y: 'center',
            width: '70%',
            height: '70%',
            background: '#634e96',
            top: 50,
            bottom: 50,
            onclose: function () {
                reportWindowClosed = true
            },
        })

        reportWindowClosed = false
        setTimeout(() => {
            graphWindow.focus()
        }, 100)
    }

    const readFromFile = (showInfo = true) => {
        if (fs.existsSync(reportFile)) {
            editor?.setData(fs.readFileSync(reportFile))
            reportRead = true
            if (showInfo)
                window.createToast(`${basename(reportFile)} file read`)
        } else {
            if (showInfo)
                window.createToast(
                    'No report file named ' + basename(reportFile),
                    'danger'
                )
        }
    }

    let autoRead = false
    $: if (reportFile && autoRead) {
        readFromFile()
    }
    let overwriteResponse = ''
    $: if (overwriteResponse) {
        console.log(overwriteResponse)
        const overwrite = overwriteResponse.toLowerCase() === 'yes'
        saveReport({ overwrite })
        overwriteResponse = ''
    }
    let overwriteDialogOpen = false
</script>

<CustomDialog
    id="report-overwrite"
    title={'Overwrite?'}
    bind:open={overwriteDialogOpen}
    bind:response={overwriteResponse}
    content={`${window.basename(
        reportFile
    )} already exists. Do you want to overwrite it?`}
/>

<div class="report_main__div align">
    <div class="notice__div">
        {mainTitle}

        <div
            style="display: flex; font-size: large; font-weight: 400; padding-right: 1em;"
            on:click={() => (showReport = !showReport)}
        >
            {showReport ? 'hideReport' : 'showReport'}
        </div>
        {#if reportWindowClosed}
            <i class="material-icons" on:click={openReport}>zoom_out_map</i>
        {/if}
    </div>

    {#if showReport}
        <div class="report_controler__div box" style="border: solid 1px #fff7;">
            <div class="report_location__div">

                <button class="button is-link" on:click={browse_folder} disabled={!enable_location_browser}
                    >Browse</button
                >
                <Textfield bind:value={location} label="report location" disabled={!enable_location_browser} />
                <Textfield
                    bind:value={savefilename}
                    label="report name"
                    style="min-width: 70%;"
                />

                <i
                    class="material-icons animated faster"
                    on:animationend={({ target }) =>
                        target.classList.remove('rotateIn')}
                    on:click={updateFiles}
                >
                    refresh
                </i>
            </div>
            <div class="btn-row">
                <slot name="btn-row" />
                <button class="button is-warning" on:click={readFromFile}
                    >read</button
                >
                <button class="button is-link" on:click={saveReport}
                    >Save</button
                >
                <CustomSwitch bind:selected={autoRead} label="autoRead" />
            </div>
        </div>
    {/if}
</div>

{#if showReport}
    <div
        class="ckeditor-svelte content"
        {id}
        use:mountEditor
        style:display={showReport ? '' : 'none'}
    />
{/if}

<style global lang="scss">
    .report-editor-div {
        display: grid;
        gap: 1em;
    }

    .ck.ck-content * {
        color: black;
    }
    .ck-editor {
        min-height: 10em;
        width: 100%;
    }

    .ck-editor__main {
        overflow: auto;

        max-height: 25em;
    }
    .ck-content .table table {
        border: 2px double black;
        background: white;
    }
    .notice__div {
        width: 100%;
        background: #634e96;
        border: 1px solid;
        border-radius: 0.2em;
        padding: 0.2em;
        font-size: 25px;
        font-weight: bold;
        display: grid;
        grid-auto-flow: column;
        grid-template-columns: 1fr auto;
        align-items: center;
    }
    .editor-div * {
        color: black;
    }
    .wb-body {
        .report-editor-div {
            padding: 1em;
            display: grid;
            gap: 1em;
            height: 100%;
            grid-template-rows: auto 1fr;

            .ck-editor__main {
                max-height: calc(100% - 5em);
            }
        }
    }

    .report_location__div {
        display: grid;

        grid-template-columns: auto 3fr 1fr auto;
        width: 100%;
        gap: 1em;

        align-items: center;
    }

    .btn-row {
        display: flex;
        gap: 1em;
    }

    .report_main__div {
        .report_controler__div {
            display: grid;
            gap: 1em;

            width: 100%;
            margin: 0;
        }
    }
</style>
