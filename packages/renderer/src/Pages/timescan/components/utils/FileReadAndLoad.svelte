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

    const readConfigDir = async () => {
        console.log('reading config dir')
        if (!window.fs.existsSync(configDir)) {
            if ($activePage === 'Kinetics') {
                return window.createToast('Invalid location', 'danger', {
                    target: 'left',
                })
            }
            return
        }

        const [files, error] = await window.fs.readdir(configDir)
        if (error) return window.handleError(error)
        config_filelists = files.filter((file) => file.endsWith(options_filter))
    }

    let config_filelists: string[] = []

    const save_data = () => {
        if (isEmpty(dataToSave)) {
            window.createToast('No data to save', 'danger')
            return
        }
        let data, error
        if (window.fs.isFile(fullfilename)) {
            ;[data, error] = window.fs.readJsonSync(fullfilename)
            console.log('file read', data, error)
            if (error) return window.handleError(error)
        }

        data ??= {}
        if (!selectedFile) return window.createToast('No file selected', 'danger')
        data[selectedFile] ??= { tags: {}, default: {} }

        if (useTaggedFile) {
            if (!tagFile) return window.createToast('No tag file selected', 'danger')
            data[selectedFile]['tags'][tagFile] = dataToSave
        } else {
            data[selectedFile]['default'] = dataToSave
        }
        ;[, error] = window.fs.outputJsonSync(fullfilename, data)
        if (error) return window.handleError(`Error writing ${filename}\n${error}`)
        return notify()
    }

    const notify = (info: string = 'saved') => window.createToast(`${filename} ${info} for ${selectedFile}`, 'success')
    const load_data = () => {
        if (!window.fs.isFile(fullfilename)) {
            return window.createToast(`File does not exists`, 'danger')
        }
        const [data, error] = window.fs.readJsonSync(fullfilename)
        if (error) return window.handleError(`Error reading ${filename}\n${error}`)
        if (!data?.[selectedFile]) return window.createToast(`No data found for ${selectedFile} file`, 'danger')

        if (useTaggedFile) {
            if (!tagFile) return window.createToast('No data found for tagged file', 'danger')
            dataToSave = data[selectedFile]['tags'][tagFile]
            return notify('loaded')
        }
        dataToSave = data[selectedFile]['default']
        return notify('loaded')
    }

    $: fullfilename = window.path.join(configDir, filename)
</script>

<div class="align box mr-auto" style="width: auto;">
    <button class="button is-warning" on:click={load_data}>Load</button>
    <TextAndSelectOptsToggler
        bind:value={filename}
        label={`config file (${options_filter})`}
        options={config_filelists}
        update={readConfigDir}
    />
    <button class="button is-link" on:click={save_data}>Save</button>
</div>

<style>
    .box {
        max-height: 400px;
        margin: 0;
        padding: 0.5em;
        border: solid 1px #fff7;
    }
</style>
