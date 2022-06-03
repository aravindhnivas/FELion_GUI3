<script>
    import { filedetails, opoMode, normMethod } from '../../functions/svelteWritables'
    import CustomIconSwitch from '$components/CustomIconSwitch.svelte'
    import Table from '$components/Table.svelte'
    import { savefile, loadfile } from '../../functions/misc'
    import computePy_func from '$src/Pages/general/computePy'
    import { get_details_func } from '../../functions/get_details'
    import { onMount } from 'svelte'

    export let felixfiles

    let toggleFileDetailsTable = false

    async function plotData({ e = null } = {}) {
        if (felixfiles.length < 1) return window.createToast('No files selected', 'danger')

        const pyfile = 'normline.getfile_details'
        const files = $opoMode ? opofiles : felixfiles
        const args = { files, normMethod: $normMethod }

        const dataFromPython = await computePy_func({ e, pyfile, args })
        if (!dataFromPython) return

        get_details_func({ dataFromPython })
        toggleFileDetailsTable = true
        console.log({ $filedetails })
    }

    function loadfiledetails() {
        const loadedfile = loadfile('filedetails')
        if (loadedfile.length < 1) return
        toggleFileDetailsTable = true
        $filedetails = loadedfile
        console.log({ loadedfile, $filedetails })
    }
    onMount(() => {
        loadfiledetails()
    })
</script>

<div class="align">
    <button class="button is-link" on:click={(e) => plotData({ e: e })}>Get details</button>
    <CustomIconSwitch bind:toggler={toggleFileDetailsTable} icons={['arrow_drop_down', 'arrow_drop_up']} />
    <button class="button is-link" on:click={() => savefile({ file: $filedetails, name: 'filedetails' })}>Save</button>
    <button class="button is-link" on:click={loadfiledetails}>Load</button>

    {#if toggleFileDetailsTable}
        <Table
            id="felix_filedetails_table"
            bind:rows={$filedetails}
            closeOption={false}
            sortOption={true}
            animateRow={false}
            head={[
                'Filename',
                'min(cm-1)',
                'max(cm-1)',
                'Trap(s)',
                'B0(ms)',
                'Res.(V)',
                'IE(eV)',
                'Temp(K)',
                'Precursor',
            ]}
            keys={['filename', 'min', 'max', 'trap', 'b0', 'res', 'ie', 'temp', 'precursor']}
        />
    {/if}
</div>
