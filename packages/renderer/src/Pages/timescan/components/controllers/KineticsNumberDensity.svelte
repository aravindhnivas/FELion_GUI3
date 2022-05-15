<script>
    import Modal from '$components/modal/Modal.svelte'
    import NumberDensity from '$src/Pages/misc/NumberDensity.svelte'
    import { createEventDispatcher } from 'svelte'

    export let nHe = ''
    export let selectedFile = ''
    export let open = false
    export let currentConfig = {}
    export let config_file = ''
    let args = {}
    const dispatch = createEventDispatcher()

    let computeNumberDensity
    let get_datas

    const save_datas = () => {
        try {
            const datas = get_datas()
            if (Object.keys(datas).length === 0) return

            const location = window.dirname(config_file)
            const filename = window.basename(config_file).split('.')[0]

            let savefilename = ''
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
                console.log(contents)
                window.fs.outputJsonSync(savefilename, contents)
                window.createToast('file saved: ' + basename(savefilename))
            }
        } catch (error) {
            window.handleError(error)
        }
    }
</script>

{#if open}
    <Modal
        bind:open
        title="{selectedFile}: Number density: {nHe} cm-3"
        id="kinetis-number-density"
        on:mounted={async () => {
            // nHe = ''
            nHe = await computeNumberDensity()
            console.log(nHe)
            console.log(config_file)
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
            />
        </svelte:fragment>

        <svelte:fragment slot="footer">
            <button class="button is-link" on:click={save_datas}>Save</button>
        </svelte:fragment>
    </Modal>
{/if}
