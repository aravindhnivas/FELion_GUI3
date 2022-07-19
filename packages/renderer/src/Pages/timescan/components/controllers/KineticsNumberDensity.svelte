<script>
    import { onMount, tick } from 'svelte'
    import Modal from '$components/modal/Modal.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import NumberDensity from '$src/Pages/misc/NumberDensity.svelte'
    import TextAndSelectOptsToggler from '$src/components/TextAndSelectOptsToggler.svelte'
    import { activePage } from '$src/sveltewritables'
    export let nHe = ''
    export let selectedFile = ''
    export let active = false
    export let configDir = ''
    export let fileCollections = []

    let filename = 'kinetics.conditions.json'
    $: savefilename = window.path.join(configDir, filename)

    let contents = {}
    const readConfigFile = async (toast = true) => {
        if (!window.fs.isFile(savefilename)) {
            if ($activePage === 'Kinetics') {
                return window.createToast('No config file found. Just compute and press save to create one', 'danger')
            }
            return
        }
        ;[contents] = window.fs.readJsonSync(savefilename)
        if (toast) window.createToast('file read: ' + window.path.basename(savefilename))
        return await compute()
    }

    onMount(async () => {
        await readConfigFile(false)
    })

    let updateCurrentConfig
    let get_datas
    const save_datas = async () => {
        try {
            const datas = await get_datas()
            if (datas === null) return window.createToast('Data is not yet full computed')
            if (Object.keys(datas).length === 0) return

            console.log(selectedFile)
            console.log(datas.added_pressure)
            console.log(datas.trap_temperature)
            // return

            contents[selectedFile] = datas
            console.log(selectedFile, contents[selectedFile])
            // await tick()
            window.fs.outputJsonSync(savefilename, contents)
            ;[contents] = window.fs.readJsonSync(savefilename)
            window.createToast(`File saved to ${window.path.basename(savefilename)} for ${selectedFile}`)
        } catch (error) {
            window.handleError(error)
        }
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
</script>

<svelte:window
    on:keydown={(e) => {
        if (active && e.ctrlKey && e.key.toLocaleLowerCase() === 's') {
            save_datas()
        }
    }}
/>
<!-- {#if active} -->
<Modal bind:active title="{selectedFile}: {nHe} cm-3" id="kinetis-number-density" on:mounted={compute}>
    <svelte:fragment slot="content">
        <NumberDensity
            bind:updateCurrentConfig
            bind:get_datas
            on:getValue={(e) => {
                nHe = e.detail.nHe
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
        <button class="button is-link" on:click={save_datas}>Save</button>
    </svelte:fragment>
</Modal>
