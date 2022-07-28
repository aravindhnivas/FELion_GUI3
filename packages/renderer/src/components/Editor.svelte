<script lang="ts">
    import { showConfirm } from '$src/components/alert/store'
    import { onDestroy } from 'svelte'
    import Textfield from '@smui/textfield'
    import { browse } from '$components/Layout.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import WinBox from 'winbox/src/js/winbox.js'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'

    export let id = window.getID()
    export let location = ''

    export let filetype = ''
    export let editor = null
    export let mount: string
    export let mainTitle = 'Report/Editor'
    export let reportRead = false
    export let savefilename = 'report'
    export let reportSaved = false
    export let showReport = false
    export let enable_location_browser = true
    export let filenameOpts: string[] = []
    export let filenameUpdate = () => {}

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

    const mountEditor = (node: HTMLElement) => {
        mountEditorFn(node)
    }

    onDestroy(() => {
        if (!editor) return
        editor.destroy()
        console.info('editor destroyed')
    })

    $: if (!showReport && editor) {
        editor.destroy()
        console.info('editor destroyed')
    }

    if (window.db.get(`${filetype}-report-md`)) {
        location = window.db.get(`${filetype}-report-md`) as string
    }

    $: reportFile = window.path.join(
        location,
        savefilename ? (savefilename.endsWith('.md') ? savefilename : `${savefilename}.md`) : ''
    )

    $: if (window.fs.isDirectory(location)) {
        window.db.set(`${filetype}-report-md`, location)
    }

    async function browse_folder() {
        const [result] = await browse()
        if (!result) return
        location = result
        window.createToast('Location updated')
    }

    const writeReport = async (info = 'saved') => {
        const contents = editor?.getData()

        const output = await window.fs.writeFile(reportFile, contents)

        if (window.fs.isError(output)) {
            return window.handleError(output)
        }
        const type = info === 'saved' ? 'success' : 'warning'
        window.createToast(`${window.path.basename(reportFile)}: report ${info}`, type)
        console.log('report writted: ', window.path.basename(reportFile))
        reportSaved = true
    }

    const saveReport = () => {
        if (!location) {
            return window.createToast('Invalid location', 'danger')
        }
        if (!window.fs.isFile(reportFile)) {
            return writeReport('saved')
        } else if (overwrite) {
            return writeReport('overwritten')
        }
        return showConfirm.push({
            title: 'Overwrite?',
            content: `Do you want to overwrite ${window.path.basename(reportFile)}?`,
            callback: (response) => {
                if (response?.toLowerCase() === 'cancel') return
                writeReport('overwritten')
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
        if (!window.fs.isFile(reportFile)) {
            if (!showInfo) return
            return window.createToast('No report file named ' + window.path.basename(reportFile), 'danger')
        }

        const fileRead = window.fs.readFileSync(reportFile)
        if (window.fs.isError(fileRead)) return window.handleError(fileRead)

        editor?.setData(fileRead)
        reportRead = true
        if (!showInfo) return

        window.createToast(`${window.path.basename(reportFile)} file read`)
    }

    let autoRead = false
    let overwrite = false
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
            <i class="material-symbols-outlined" on:click={openReport}>zoom_out_map</i>
        {/if}
    </div>

    {#if showReport}
        <div class="report_controler__div box" style="border: solid 1px #fff7;">
            <div class="report_location__div">
                <button class="button is-link" on:click={browse_folder} disabled={!enable_location_browser}
                    >Browse</button
                >
                <Textfield bind:value={location} label="report location" disabled={!enable_location_browser} />
                <TextAndSelectOptsToggler
                    bind:value={savefilename}
                    label="report name"
                    update={filenameUpdate}
                    options={filenameOpts}
                    auto_init={true}
                />
            </div>

            <div class="btn-row">
                <slot name="btn-row" />
                <button class="button is-warning" on:click={() => readFromFile()}>read</button>
                <button class="button is-link" on:click={saveReport}>Save</button>
                <CustomSwitch bind:selected={autoRead} label="autoRead" />
                <CustomSwitch bind:selected={overwrite} label="overwrite" />
            </div>
        </div>
    {/if}
</div>

{#if showReport}
    <div use:mountEditor class="ckeditor-svelte content" {id} style:display={showReport ? '' : 'none'} />
{/if}
