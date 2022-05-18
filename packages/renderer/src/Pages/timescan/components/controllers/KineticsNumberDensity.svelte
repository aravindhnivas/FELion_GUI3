<script>
    import { tick } from 'svelte'
    import Modal from '$components/modal/Modal.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import TextAndSwitchToggler from '$components/TextAndSwitchToggler.svelte'
    import NumberDensity from '$src/Pages/misc/NumberDensity.svelte'

    export let nHe = ''
    export let selectedFile = ''
    export let active = false
    export let config_content = {}
    export let config_file = ''

    export let fileCollections = []
    export let config_filelists = []
    export let readConfigDir = () => {}

    let currentConfig = {}
    $: if (selectedFile) {
        currentConfig = config_content[selectedFile]
    }
    let savefilename = ''
    let computeNumberDensity
    let get_datas
    const save_datas = () => {
        try {
            const datas = get_datas()
            if (Object.keys(datas).length === 0) return

            const location = window.dirname(config_file)
            const filename = window.basename(config_file).split('.')[0]

            // let savefilename = ''
            if (window.fs.isDirectory(location)) {
                savefilename = window.pathJoin(
                    location,
                    `${filename}.conditions.json`
                )
                let contents = {}
                if (window.fs.isFile(savefilename)) {
                    ;[contents] = window.fs.readJsonSync(savefilename)
                }
                contents[selectedFile] = datas
                console.log(contents[selectedFile])
                window.fs.outputJsonSync(savefilename, contents)
                window.createToast('file saved: ' + basename(savefilename))
            }
        } catch (error) {
            window.handleError(error)
        }
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
        on:mounted={async () => {
            nHe = await computeNumberDensity()
        }}
    >
        <svelte:fragment slot="content">
            <NumberDensity
                bind:computeNumberDensity
                bind:get_datas
                {currentConfig}
                on:getValue={(e) => {
                    nHe = e.detail.nHe
                }}
            >
                <svelte:fragment slot="header" let:updateCurrentConfig>
                    <TextAndSwitchToggler
                        bind:value={savefilename}
                        label="config file (*.conditions.json)"
                        options={config_filelists.filter((f) =>
                            f.endsWith('.conditions.json')
                        )}
                        update={readConfigDir}
                    />
                    <CustomSelect
                        on:change={async () => {
                            await tick()
                            updateCurrentConfig(currentConfig)
                        }}
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
