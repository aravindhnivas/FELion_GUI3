<script lang="ts">
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'
    import { isEmpty } from 'lodash-es'
    import Textfield from '@smui/textfield'
    import MenuSurface from '@smui/menu-surface'
    import type { MenuSurfaceComponentDev } from '@smui/menu-surface'
    import { tick } from 'svelte'

    export let configDir: string = ''
    export let selectedFile: string = ''
    export let options_filter: string = '.json'
    export let useTaggedFile: boolean = false
    export let useParamsFile: boolean = false
    export let tagFile: string = ''
    export let filename = ''
    export let data_loaded = false
    export let dataToSave
    export let singleFilemode = false

    let surface: MenuSurfaceComponentDev

    console.log({ filename, configDir })
    const toastOpts = {
        target: 'left',
    }

    const save_data = () => {
        if (isEmpty(dataToSave)) {
            window.createToast('No data to save', 'danger', toastOpts)
            return
        }

        if (!filename.endsWith(options_filter)) {
            filename = `${filename}${options_filter}`
        }
        const savefilename = window.path.join(configDir, filename)

        if (singleFilemode) {
            const data = { default: dataToSave }
            const [, error] = window.fs.outputJsonSync(savefilename, data)
            if (error) return window.handleError(`Error writing ${filename}\n${error}`)
            return notify()
        }

        let data, error
        if (window.fs.isFile(savefilename)) {
            ;[data, error] = window.fs.readJsonSync(savefilename)
            console.log('file read', data, error)
            if (error) return window.handleError(error)
        }

        data ??= {}
        if (!selectedFile) return window.createToast('No file selected', 'danger', toastOpts)
        data[selectedFile] ??= { tags: {}, default: {} }

        if (useTaggedFile) {
            if (!tagFile) return window.createToast('No tag file selected', 'danger', toastOpts)
            data[selectedFile]['tags'][tagFile] = dataToSave
        } else {
            data[selectedFile]['default'] = dataToSave
        }

        ;[, error] = window.fs.outputJsonSync(savefilename, data)
        if (error) return window.handleError(`Error writing ${filename}\n${error}`)
        data_loaded = true
        return notify()
    }

    const notify = (info: string = 'saved') => {
        console.log({ dataToSave })
        window.createToast(`${filename} ${info} for ${selectedFile}`, 'success', toastOpts)
    }

    export const load_data = (toast = true) => {
        // await tick()

        data_loaded = false
        const loadfilename = window.path.join(configDir, filename)

        if (!window.fs.isFile(loadfilename)) {
            return window.createToast(`File does not exists`, 'danger', toastOpts)
        }

        const [data, error] = window.fs.readJsonSync(loadfilename)
        if (error) return window.handleError(`Error reading ${filename}\n${error}`)

        if (singleFilemode) {
            if (!data.default) return window.createToast(`default-mode: No data found`, 'danger', toastOpts)
            dataToSave = data.default
            data_loaded = true
            if (toast) notify('loaded')
            return
        }

        if (!data?.[selectedFile]) {
            return window.createToast(`No data found for ${selectedFile} file`, 'danger', toastOpts)
        }
        if (useTaggedFile) {
            if (!tagFile) {
                return window.createToast(`Invalid tagFile name`, 'danger', toastOpts)
            }
            if (!data[selectedFile]?.['tags']) {
                return window.createToast('No tag column created for this file', 'danger', toastOpts)
            }
            if (!data[selectedFile]['tags'][tagFile]) {
                return window.createToast(`tag-mode: No data found for ${selectedFile} file`, 'danger', toastOpts)
            }

            data_loaded = true
            dataToSave = data[selectedFile]['tags'][tagFile]
            if (toast) notify('loaded')
            return
        }

        if (!data[selectedFile]['default']) {
            return window.createToast(`default-mode: No data found for ${selectedFile} file`, 'danger', toastOpts)
        }

        dataToSave = data[selectedFile]['default']
        data_loaded = true
        if (toast) notify('loaded')
        return
    }
    // $: console.log({ data_loaded })
    $: if (selectedFile && (useParamsFile || useTaggedFile)) {
        load_data(false)
    }
</script>

<div class="container mb-5">
    <button class="button is-warning" on:click={load_data}>Load</button>
    <TextAndSelectOptsToggler
        bind:value={filename}
        label={`config file (*${options_filter})`}
        lookFor={options_filter}
        lookIn={configDir}
    />
    <button class="button is-link" on:click={save_data}>Save</button>
    <MenuSurface
        style="background: #9666db;"
        bind:this={surface}
        anchorCorner="BOTTOM_START"
        anchorMargin={{ top: 0, right: 0, bottom: 0, left: 0 }}
    >
        <div class="align p-5">
            <Textfield bind:value={configDir} label="save location" />
        </div>
    </MenuSurface>
    <span class="material-icons" on:click={() => surface.setOpen(true)}> help </span>
</div>

<style>
    .container {
        align-items: center;
        display: flex;
        gap: 1em;
        margin-left: auto;
    }
</style>
