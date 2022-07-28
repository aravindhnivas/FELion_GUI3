<script>
    import Textfield from '@smui/textfield'
    import ModalTable from '$components/ModalTable.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'
    // import FileReadAndLoad from '$components/FileReadAndLoad.svelte'
    import { plotlyEventsInfo } from '$src/js/functions'

    export let varyAll = false
    export let active = false
    export let paramsTable = []
    export let fitMethod = 'gaussian'
    export let currentLocation = ''

    const keys = ['freq', 'amp', 'fG', 'fL']
    let savefilename = 'thz_fit_params.json'
    $: configDir = window.path.resolve(currentLocation, 'CONFIGS')
    $: saveParamsToFile = window.path.join(configDir, savefilename)

    const saveConfig = () => {
        if (!window.fs.isDirectory(configDir)) {
            window.fs.mkdirSync(configDir)
        }
        const dataToSave = { units: { freq: 'GHz', fG: 'MHz', fL: 'MHz' } }
        paramsTable.forEach((params) => {
            const { freq, amp, fG, fL } = params
            dataToSave[freq] = { amp, fG, fL }
        })
        const result = window.fs.outputJsonSync(saveParamsToFile, dataToSave)
        if (window.fs.isError(result)) return window.handleError(result)
        window.createToast('file saved')
    }

    const loadConfig = () => {
        if (!window.fs.isFile(saveParamsToFile)) return window.createToast('No files saved yet', 'danger')
        const readParams = window.fs.readJsonSync(saveParamsToFile)
        if (window.fs.isError(readParams)) return window.handleError(readParams)
        const frequencies = Object.keys(readParams).filter((key) => key !== 'units')
        paramsTable = frequencies.map((freq) => {
            const { amp, fG, fL } = readParams[freq]
            const id = window.getID()
            return { freq, amp, fG, fL, id }
        })
        window.createToast('Config loaded', 'warning')
    }

    const getValuesFromAnnotations = () => {
        paramsTable = []
        const annotations = $plotlyEventsInfo.thzPlot.annotations
        annotations.forEach((annotation) => {
            const { x, y } = annotation
            const fG = fitMethod === 'gaussian' || fitMethod === 'voigt' ? 1 : 0
            const fL = fitMethod === 'lorentz' || fitMethod === 'voigt' ? 1 : 0
            const newParams = {
                freq: Number(x).toFixed(6),
                amp: Number(y).toFixed(2),
                fG,
                fL,
                id: window.getID(),
            }
            paramsTable = [...paramsTable, newParams]
        })
    }
</script>

<ModalTable bind:active title="Config table" bind:rows={paramsTable} {keys} sortOption={true}>
    <svelte:fragment slot="header">
        <Textfield bind:value={savefilename} label="savefilename" style="width: 100%;" />
        <!-- <FileReadAndLoad {configDir} selectedFile={savefilename} bind:dataToSave={paramsTable} /> -->
    </svelte:fragment>

    <svelte:fragment slot="footer">
        <div class="align">
            <CustomCheckbox bind:value={varyAll} label="varyAll" />
            <button class="button is-link" on:click={getValuesFromAnnotations}>getValuesFromAnnotations</button>
            <button class="button is-link" on:click={saveConfig}>Save</button>
            <button class="button is-link" on:click={loadConfig}>Load</button>
            <button class="button is-danger" on:click={() => (paramsTable = [])}>Clear ALL</button>
        </div>
    </svelte:fragment>
</ModalTable>
