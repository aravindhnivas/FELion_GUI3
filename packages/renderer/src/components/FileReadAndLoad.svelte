<script lang="ts">
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'
    import { isEmpty, uniqBy } from 'lodash-es'
    import Textfield from '@smui/textfield'
    import MenuSurface from '@smui/menu-surface'
    import type { MenuSurfaceComponentDev } from '@smui/menu-surface'
    // import { tick } from 'svelte'

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
    export let singleFilemode_ObjectKey = null
    export let uniqFilter = null

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
            let saveDataForFile = null
            if (singleFilemode_ObjectKey) {
                saveDataForFile = {}
                dataToSave.forEach((data) => {
                    saveDataForFile[data[singleFilemode_ObjectKey]] = {}
                    for (const key in data) {
                        if (key !== singleFilemode_ObjectKey) {
                            saveDataForFile[data[singleFilemode_ObjectKey]] = {
                                [key]: data[key],
                                ...saveDataForFile[data[singleFilemode_ObjectKey]],
                            }
                        }
                    }
                })
            }

            saveDataForFile ??= { default: dataToSave }

            const result = window.fs.outputJsonSync(savefilename, saveDataForFile)
            if (window.fs.isError(result)) return window.handleError(`Error writing ${filename}\n${result.message}`)
            return notify()
        }

        let data = {}
        if (window.fs.isFile(savefilename)) {
            data = window.fs.readJsonSync(savefilename)
            if (window.fs.isError(data)) return window.handleError(data)
        }

        // data ??= {}
        if (!selectedFile) return window.createToast('No file selected', 'danger', toastOpts)
        data[selectedFile] ??= { tags: {}, default: {} }

        if (useTaggedFile) {
            if (!tagFile) return window.createToast('No tag file selected', 'danger', toastOpts)
            data[selectedFile]['tags'][tagFile] = dataToSave
        } else {
            data[selectedFile]['default'] = dataToSave
        }

        const result = window.fs.outputJsonSync(savefilename, data)
        if (window.fs.isError(result)) return window.handleError(`Error writing ${filename}\n${result.message}`)
        data_loaded = true
        return notify()
    }

    const notify = (info: string = 'saved') => {
        console.log({ dataToSave })
        if (singleFilemode) {
            return window.createToast(`${filename} ${info}`, 'success', toastOpts)
        }
        window.createToast(`${filename} ${info} for ${selectedFile}`, 'success', toastOpts)
    }

    export const load_data = (toast = true) => {
        // await tick()

        data_loaded = false
        const loadfilename = window.path.join(configDir, filename)

        if (!window.fs.isFile(loadfilename)) {
            return window.createToast(`File does not exists. Save it first.`, 'danger', toastOpts)
        }

        const data = window.fs.readJsonSync(loadfilename)
        if (window.fs.isError(data)) return window.handleError(`Error reading ${filename}\n${data.message}`)

        if (singleFilemode) {
            if (singleFilemode_ObjectKey) {
                const keys = Object.keys(data)

                if (keys.length === 0) return window.createToast(`No data found`, 'danger', toastOpts)

                for (const key of keys) {
                    dataToSave = [{ [singleFilemode_ObjectKey]: key, ...data[key] }, ...dataToSave]
                }

                if (uniqFilter) {
                    dataToSave = uniqBy(dataToSave, uniqFilter)
                }
                if (toast) notify('loaded')
                return
            }

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

    $: if (!singleFilemode && selectedFile && (useParamsFile || useTaggedFile)) {
        load_data(false)
    }
</script>

<div class="container mb-5">
    <button class="button is-warning" on:click={() => load_data()}>Load</button>
    <TextAndSelectOptsToggler
        bind:value={filename}
        label={`config file (*${options_filter})`}
        lookFor={options_filter}
        lookIn={configDir}
        auto_init={true}
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
    <span role="presentation" class="material-symbols-outlined" on:click={() => surface.setOpen(true)}> help </span>
</div>

<style>
    .container {
        align-items: center;
        display: flex;
        gap: 1em;
        margin-left: auto;
    }
</style>
