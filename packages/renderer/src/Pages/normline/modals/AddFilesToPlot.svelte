<script lang="ts">
    import { addTraces } from 'plotly.js-basic-dist'
    import Textfield from '@smui/textfield'
    import Modal from '$components/Modal.svelte'
    // import { browse } from '$components/Layout.svelte'
    import { graphDiv } from '../functions/svelteWritables'
    import computePy_func from '$src/Pages/general/computePy'

    export let active = false
    export let fileChecked = []
    export let addedFileCol = '0, 1'

    export let addedFileScale = 1000
    export let addedfiles: string[] = []
    export let addedFile = {}
    export let extrafileAdded = 0

    function addFileSelection() {
        const result = window.browse({ dir: false, multiple: true })
        if (!result) return
        addedfiles = addedFile['files'] = result
        window.createToast('Files added')
    }

    function plotData({ e = null } = {}) {
        const pyfile = 'normline.addTrace'
        let args
        if (addedFile.files < 1) return window.createToast('No files selected', 'danger')
        extrafileAdded += addedfiles.length
        ;(addedFile['col'] = addedFileCol), (addedFile['N'] = fileChecked.length + extrafileAdded)

        addedFile['scale'] = addedFileScale
        args = addedFile

        computePy_func({ e, pyfile, args }).then((dataFromPython) => {
            addTraces($graphDiv, dataFromPython)
            window.createToast('Graph Plotted', 'success')
            active = false
        })
    }
</script>

{#if active}
    <Modal bind:active title="Add file to plot">
        <div class="align" slot="content">
            <Textfield bind:value={addedFileCol} label="Columns" />
            <Textfield bind:value={addedFileScale} label="ScaleY" />
            <button on:click={addFileSelection} class="button is-link">Browse</button>
        </div>
        <button slot="footerbtn" class="button is-link" on:click={(e) => plotData({ e: e })}>Add</button>
    </Modal>
{/if}
