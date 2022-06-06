<script lang="ts">
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'
    import { activePage } from '$src/sveltewritables'
    import { isEmpty } from 'lodash-es'

    export let configDir: string = ''
    export let selectedFile: string = ''
    export let options_filter: string = '.json'
    export let useTaggedFile: boolean = false
    export let tagFile: string = ''
    export let filename = ''

    export let dataToSave
    const toastOpts = {
        target: 'left',
    }
    const readConfigDir = async () => {
        console.log('reading config dir')
        if (!window.fs.isDirectory(configDir)) {
            if ($activePage === 'Kinetics') {
                return window.createToast('Invalid location', 'danger', toastOpts)
            }
            return
        }

        const [files, error] = await window.fs.readdir(configDir)
        if (error) return window.handleError(error)
        config_filelists = files.filter((file) => file.endsWith(options_filter))
        console.log(config_filelists, files, options_filter)
    }

    let config_filelists: string[] = []

    const save_data = () => {
        if (isEmpty(dataToSave)) {
            window.createToast('No data to save', 'danger', toastOpts)
            return
        }
        let data, error
        if (window.fs.isFile(fullfilename)) {
            ;[data, error] = window.fs.readJsonSync(fullfilename)
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
        ;[, error] = window.fs.outputJsonSync(fullfilename, data)
        if (error) return window.handleError(`Error writing ${filename}\n${error}`)

        return notify()
    }
    let data_loaded = false
    const notify = (info: string = 'saved') => {
        data_loaded = true
        window.createToast(`${filename} ${info} for ${selectedFile}`, 'success', toastOpts)
    }

    const load_data = () => {
        if (!window.fs.isFile(fullfilename)) {
            return window.createToast(`File does not exists`, 'danger', toastOpts)
        }
        const [data, error] = window.fs.readJsonSync(fullfilename)

        if (error) return window.handleError(`Error reading ${filename}\n${error}`)
        if (!data?.[selectedFile])
            return window.createToast(`No data found for ${selectedFile} file`, 'danger', toastOpts)

        if (useTaggedFile) {
            if (!tagFile) return window.createToast('No data found for tagged file', 'danger', toastOpts)
            dataToSave = data[selectedFile]['tags'][tagFile]
            return notify('loaded')
        }

        dataToSave = data[selectedFile]['default']
        data_loaded = true
        return notify('loaded')
    }

    $: fullfilename = window.path.join(configDir, filename)
    $: if (selectedFile) {
        data_loaded = false
    }
</script>

<div class="container box ml-auto mb-5">
    <i class="material-icons mr-auto">{data_loaded ? 'done' : 'sync_problem'}</i>
    <button class="button is-warning" on:click={load_data}>Load</button>
    <TextAndSelectOptsToggler
        bind:value={filename}
        label={`config file (*${options_filter})`}
        options={config_filelists}
        update={readConfigDir}
    />
    <button class="button is-link" on:click={save_data}>Save</button>
</div>

<style>
    .container {
        align-items: center;
        display: flex;
        gap: 1em;
        width: 100%;
        justify-content: flex-end;
    }
    .box {
        max-height: 400px;
        margin: 0;
        padding: 0.5em;
        border: solid 1px #fff7;
    }
</style>
