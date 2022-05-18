<script>
    import { onMount } from 'svelte'
    import Modal from '$components/modal/Modal.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import NumberDensity from '$src/Pages/misc/NumberDensity.svelte'
    import TextAndSwitchToggler from '$components/TextAndSwitchToggler.svelte'

    export let nHe = ''
    export let selectedFile = ''
    export let active = false
    export let config_location = ''
    export let fileCollections = []

    export let config_filelists = []
    export let readConfigDir = () => {}

    let filename = 'kinetics.conditions.json'
    $: savefilename = pathJoin(config_location, filename)

    let contents = {}
    const readConfigFile = () => {
        if (!fs.isFile(savefilename)) {
            return window.createToast(
                'No config file found. Just compute and press save to create one',
                'danger'
            )
        }
        ;[contents] = fs.readJsonSync(savefilename)
        if (active) {
            window.createToast('file read: ' + basename(savefilename))
            compute()
        }
    }

    let mounted = false
    onMount(() => {
        mounted = true
        readConfigFile()
    })

    let updateCurrentConfig
    let get_datas
    const save_datas = () => {
        try {
            const datas = get_datas()
            if (Object.keys(datas).length === 0) return
            contents[selectedFile] = datas
            console.log(contents[selectedFile])
            fs.outputJsonSync(savefilename, contents)
            window.createToast('file saved: ' + basename(savefilename))
        } catch (error) {
            window.handleError(error)
        }
    }

    const compute = () => {
        const currentConfig = contents?.[selectedFile]
        if (active && !currentConfig) {
            return window.createToast(
                `config not found for selected file: ${selectedFile}`,
                'danger'
            )
        }
        updateCurrentConfig(currentConfig)
    }
</script>

<svelte:window
    on:keydown={(e) => {
        if (active && e.ctrlKey && e.key.toLocaleLowerCase() === 's') {
            save_datas()
        }
    }}
/>
{#if active}
    <Modal
        bind:active
        title="{selectedFile}: {nHe} cm-3"
        id="kinetis-number-density"
        on:mounted={compute}
    >
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
                        <TextAndSwitchToggler
                            bind:value={filename}
                            label="config file (*.conditions.json)"
                            options={config_filelists.filter((f) =>
                                f.endsWith('.conditions.json')
                            )}
                            update={readConfigDir}
                        />

                        <button class="button is-link" on:click={readConfigFile}
                            >Read file</button
                        >

                        <CustomSelect
                            on:change={compute}
                            bind:value={selectedFile}
                            label="Filename"
                            options={fileCollections}
                        />
                        <span
                            class="tag is-success"
                            class:is-danger={!contents?.[selectedFile]}
                        >
                            config {contents?.[selectedFile]
                                ? 'found'
                                : 'not found'}
                        </span>
                    </div>
                </svelte:fragment>
            </NumberDensity>
        </svelte:fragment>
        <svelte:fragment slot="footer">
            <button class="button is-link" on:click={save_datas}>Save</button>
        </svelte:fragment>
    </Modal>
{/if}
