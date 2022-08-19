<script>
    import { onMount } from 'svelte'
    import Modal from '$components/modal/Modal.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import NumberDensity from '$src/Pages/misc/NumberDensity.svelte'
    import TextAndSelectOptsToggler from '$src/components/TextAndSelectOptsToggler.svelte'
    import { activePage } from '$src/sveltewritables'
    // import { browse } from '$components/Layout.svelte'

    export let nHe = ''
    export let selectedFile = ''
    export let active = false

    export let configDir = ''
    export let fileCollections = []

    let filename = 'kinetics.conditions.json'
    $: savefilename = window.path.join(configDir, filename)
    let contents = {}

    $: if (window.fs.isFile(savefilename)) {
        readConfigFile()
    }

    const readConfigFile = async (toast = true) => {
        if (!window.fs.isFile(savefilename)) {
            if ($activePage === 'Kinetics') {
                return window.createToast('No config file found. Just compute and press save to create one', 'danger')
            }
            return
        }
        contents = window.fs.readJsonSync(savefilename)
        if (window.fs.isError(contents)) return window.handleError(contents)
        if (toast) window.createToast('file read: ' + window.path.basename(savefilename))
        return await compute()
    }

    onMount(async () => {
        await readConfigFile(false)
    })

    let updateCurrentConfig
    let get_datas

    const save_datas = async () => {
        if (!get_datas) return window.createToast('No datas computed', 'danger')
        if (get_datas === null) return window.createToast('Data is not yet full computed')
        if (Object.keys(get_datas).length === 0) return

        contents[selectedFile] = get_datas

        const result = window.fs.outputJsonSync(savefilename, contents)
        if (window.fs.isError(result)) return window.handleError(result)

        contents = window.fs.readJsonSync(savefilename)
        if (window.fs.isError(contents)) return window.handleError(contents)

        window.createToast(`File saved to ${window.path.basename(savefilename)} for ${selectedFile}`)
    }

    const compute = async () => {
        if (!updateCurrentConfig) return
        const currentConfig = contents?.[selectedFile]
        if (active && !currentConfig) return
        return await updateCurrentConfig(currentConfig)
    }

    $: if (selectedFile) {
        compute()
    }

    let config_file = ''
    const browseFromConfigFile = () => {
        config_file = ''
        const [result] = window.browse({ filetype: 'configs.json', dir: false })
        if (!result) return
        config_file = result
    }

    const loadFromConfigFile = async () => {
        if (!config_file) return window.createToast('No config file loaded')
        const config_contents = window.fs.readJsonSync(config_file)
        if (window.fs.isError(config_contents)) return window.handleError(config_contents)
        window.createToast(`File read: ${window.path.basename(config_file)}`)

        const keys = Object.keys(config_contents)
        const contents = {}
        for (const key of keys) {
            const config = config_contents[key]
            set_minimal_config?.(config)
            const datas = await computeNumberDensity(null, true)
            contents[key] = datas
        }

        const result = window.fs.outputJsonSync(savefilename, contents)
        if (window.fs.isError(result)) return window.handleError(result)
        window.createToast(`File saved to ${window.path.basename(savefilename)}`, 'success')
        await readConfigFile()
    }

    let computeNumberDensity = null
    let set_minimal_config = null
</script>

<svelte:window
    on:keydown={(e) => {
        if (active && e.ctrlKey && e.key.toLocaleLowerCase() === 's') {
            save_datas()
        }
    }}
/>
<Modal bind:active title="{selectedFile}: {nHe} cm-3" id="kinetis-number-density" on:mounted={compute}>
    <svelte:fragment slot="content">
        <NumberDensity
            bind:computeNumberDensity
            bind:set_minimal_config
            bind:updateCurrentConfig
            on:getValue={(e) => {
                nHe = e.detail.nHe
            }}
            on:fullargs={(e) => {
                get_datas = e.detail.datas
            }}
        >
            <svelte:fragment slot="header">
                <div class="align h-center">
                    <TextAndSelectOptsToggler
                        bind:value={filename}
                        label="config file (*.conditions.json)"
                        lookFor=".conditions.json"
                        lookIn={configDir}
                    />
                    <button class="button is-link" on:click={readConfigFile}>Read file</button>
                    <CustomSelect bind:value={selectedFile} label="Filename" options={fileCollections} />
                    <span class="tag is-success" class:is-danger={!contents?.[selectedFile]}>
                        config {contents?.[selectedFile] ? 'found' : 'not found'}
                    </span>
                </div>
            </svelte:fragment>
        </NumberDensity>
    </svelte:fragment>
    <svelte:fragment slot="footer">
        <button class="button is-warning" on:click={browseFromConfigFile}>browse config file</button>
        <button class="button is-warning" on:click={loadFromConfigFile}>load config file</button>
        <button class="button is-success has-green-background" on:click={save_datas}>Save</button>
    </svelte:fragment>
</Modal>
