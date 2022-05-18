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
    onMount(() => {
        if (fs.isFile(savefilename)) {
            ;[contents] = fs.readJsonSync(savefilename)
        }
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
        const currentConfig = contents[selectedFile]
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
        title="{selectedFile}: Number density: {nHe} cm-3"
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
                    <TextAndSwitchToggler
                        bind:value={filename}
                        label="config file (*.conditions.json)"
                        options={config_filelists.filter((f) =>
                            f.endsWith('.conditions.json')
                        )}
                        update={readConfigDir}
                    />

                    <CustomSelect
                        on:change={compute}
                        bind:value={selectedFile}
                        label="Filename"
                        options={fileCollections}
                    />
                </svelte:fragment>
            </NumberDensity>
        </svelte:fragment>
        <svelte:fragment slot="footer">
            <button class="button is-link" on:click={save_datas}>Save</button>
        </svelte:fragment>
    </Modal>
{/if}
