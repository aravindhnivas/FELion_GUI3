<script>
    import { showConfirm } from '$src/components/alert/store'
    import { onDestroy, onMount } from 'svelte'
    import Textfield from '@smui/textfield'
    import { browse } from '$components/Layout.svelte'
    import WinBox from 'winbox/src/js/winbox.js'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    // import { resizableDiv } from '$src/js/resizableDiv.js'

    export let id = getID()
    export let location = ''
    export let filetype = ''
    export let editor = null

    export let mount = null
    export let mainTitle = 'Report/Editor'
    export let reportRead = false
    export let savefilename = 'report'
    export let reportSaved = false
    export let showReport = false
    export let enable_location_browser = true

    async function mountEditorFn(node) {
        try {
            editor = await ClassicEditor.create(node, {
                toolbar: { shouldNotGroupWhenFull: true },
            })
            readFromFile(false)
        } catch (error) {
            window.handleError(error)
        }
    }

    const mountEditor = (node) => {
        mountEditorFn(node)
    }
    // onMount(()=>{
    //     mountEditor(document.getElementById(`${filetype}-editor`))
    // })

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

    const writeReport = async () => {
        const contents = editor.getData()
        const [, error] = await fs.writeFile(reportFile, contents, 'utf8')
        if (error) {
            return window.createToast("Report couldn't be saved.", 'danger')
        }
        window.createToast('Report saved', 'success')
        console.log('report writted: ', basename(reportFile))
        reportSaved = true
    }

    const saveReport = () => {
        if (!location) {
            return window.createToast('Invalid location', 'danger')
        }
        if (!fs.existsSync(reportFile)) return writeReport()
        return showConfirm.push({
            title: 'Overwrite?',
            content: `Do you want to overwrite ${basename(reportFile)}?`,
            callback: (response) => {
                if (response?.toLowerCase() === 'cancel') return
                writeReport()
            },
        })
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
        if (!fs.existsSync(reportFile)) {
            if (!showInfo) return
            return window.createToast(
                'No report file named ' + basename(reportFile),
                'danger'
            )
        }
        editor?.setData(fs.readFileSync(reportFile))
        reportRead = true
        if (!showInfo) return

        window.createToast(`${basename(reportFile)} file read`)
    }

    let autoRead = false

    $: if (reportFile && autoRead) {
        readFromFile()
    }
</script>

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
                <button
                    class="button is-link"
                    on:click={browse_folder}
                    disabled={!enable_location_browser}>Browse</button
                >
                <Textfield
                    bind:value={location}
                    label="report location"
                    disabled={!enable_location_browser}
                />
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
        use:mountEditor
        class="ckeditor-svelte content"
        {id}
        style:display={showReport ? '' : 'none'}
    />
{/if}
