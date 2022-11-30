<script lang="ts">
    import { opoMode, normMethods, Ngauss_sigma, felixopoLocation } from './normline/functions/svelteWritables'

    import AddFilesToPlot from './normline/modals/AddFilesToPlot.svelte'
    import FrequencyTable from './normline/components/FrequencyTable.svelte'
    import InitFunctionRow from './normline/widgets/preprocessing/InitFunctionRow.svelte'
    import OPORow from './normline/widgets/preprocessing/OPORow.svelte'
    import AdjustInitialGuess from './normline/modals/AdjustInitialGuess.svelte'
    import TheoryRow from './normline/widgets/preprocessing/TheoryRow.svelte'
    import GetFileInfoTable from './normline/widgets/preprocessing/GetFileInfoTable.svelte'
    import WriteFunctionContents from './normline/widgets/postprocessing/WriteFunctionContents.svelte'
    import ExecuteFunctionContents from './normline/widgets/postprocessing/ExecuteFunctionContents.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import Layout from '$components/Layout.svelte'
    import CustomRadio from '$components/CustomRadio.svelte'
    import { deleteTraces } from 'plotly.js-basic-dist'
    import CustomSegBtn from '$src/components/CustomSegBtn.svelte'
    ///////////////////////////////////////////////////////////////////////

    export let id = 'Normline'
    export let display = 'grid'
    export let saveLocationToDB = true

    const filetype = 'felix'
    const uniqueID = `${id}-${window.getID()}`

    setContext('uniqueID', uniqueID)
    setContext('saveLocationToDB', saveLocationToDB)

    // let display = window.db.get('active_tab') === id ? 'block' : 'none'

    let fileChecked = []
    // let toggleBrowser = false;
    let currentLocation = ''

    $: felixfiles = fileChecked.map((file) => window.path.resolve(currentLocation, file))
    // $: console.log(`${filetype} currentlocation: \n${currentLocation}`)

    ///////////////////////////////////////////////////////////////////////
    let showTheory = true
    let graphPlotted = false
    let overwrite_expfit = true
    let writeFile = true
    let OPOfilesChecked = []
    let writeFileName = 'average_normline.dat'

    $: plottedFiles = $opoMode[uniqueID]
        ? OPOfilesChecked.map((file) => file.split('.')[0]) || []
        : fileChecked.map((file) => file.split('.')[0]) || []
    $: output_namelists = [
        'averaged',
        ...plottedFiles,
        ...addedfiles.map((file) => window.path.basename(file)).map((file) => file.split('.')[0]),
    ]

    // OPO
    let OPOLocation = (window.db.get('ofelix_location') as string) || currentLocation
    let opofiles = []

    let theoryLocation = (window.db.get('theoryLocation') as string) || currentLocation

    $: $felixopoLocation[uniqueID] = $opoMode[uniqueID] ? OPOLocation : currentLocation
    $: $Ngauss_sigma[uniqueID] = $opoMode[uniqueID] ? 2 : 5

    let addFileModal = false
    let addedFile = {}
    let addedfiles = []
    let addedFileCol = '0, 1'
    let addedFileScale = 1
    let extrafileAdded = 0

    $: console.log(`Extrafile added: ${extrafileAdded}`)
    $: currentGraphID = $opoMode[uniqueID] ? `${uniqueID}-opoRelPlot` : `${uniqueID}-avgplot`
    function removeExtraFile() {
        for (let i = 0; i < extrafileAdded + 1; i++) {
            try {
                deleteTraces(currentGraphID, [-1])

                extrafileAdded--
                addedfiles = addedfiles.slice(0, addedfiles.length - 1)
            } catch (err) {
                console.log('The plot is empty')
            }
        }
    }

    $: fullfiles = $opoMode[uniqueID]
        ? [...opofiles, ...addedfiles, window.path.resolve(currentLocation, 'averaged.felix')]
        : [...felixfiles, ...addedfiles, window.path.resolve(currentLocation, 'averaged.felix')]

    let activateConfigModal = false
    let modalActivate = false
    let adjustPeakTrigger = false

    let plotfile = 'average'

    // let showMoreOptions = false

    let showOPO = true
    let showFELIX = true
    let showRawData = true
    let showPowerData = true

    let show_graphs = [
        { name: 'Raw data', selected: true },
        { name: 'Power-Calib', selected: true },
        { name: 'FELIX', selected: true },
        { name: 'OPO', selected: true },
        { name: 'Theory', selected: true },
    ]
    $: if (show_graphs) {
        showFELIX = show_graphs.find((graph) => graph.name === 'FELIX').selected
        showOPO = show_graphs.find((graph) => graph.name === 'OPO').selected
        showTheory = show_graphs.find((graph) => graph.name === 'Theory').selected
        showRawData = show_graphs.find((graph) => graph.name === 'Raw data').selected
        showPowerData = show_graphs.find((graph) => graph.name === 'Power-Calib').selected
    }

    $: plotfileOptions = $opoMode[uniqueID] ? [...OPOfilesChecked, 'average'] : [...fileChecked, 'average']

    onMount(() => {
        opoMode.init(uniqueID)
        Ngauss_sigma.init(uniqueID)
        felixopoLocation.init(uniqueID)
        console.warn('Normline mounted')
    })
    onDestroy(() => {
        opoMode.remove(uniqueID)
        Ngauss_sigma.remove(uniqueID)
        felixopoLocation.remove(uniqueID)
        console.warn('Normline destroyed')
    })

    let felix_toggle = true
    let opo_toggle = true
    let theory_toggle = true

    let showall = true
    let normMethod: string = normMethods[1]
    let theoryRow = false
</script>

<AddFilesToPlot
    {fileChecked}
    bind:addedfiles
    bind:addedFile
    bind:addedFileCol
    bind:addedFileScale
    bind:extrafileAdded
    bind:active={addFileModal}
/>

<AdjustInitialGuess bind:active={modalActivate} on:save={() => (adjustPeakTrigger = true)} />

<Layout {id} {display} {filetype} {graphPlotted} bind:fileChecked bind:currentLocation bind:activateConfigModal>
    <svelte:fragment slot="toggle_row">
        {#if $opoMode[uniqueID]}
            <span class="tag" style="border: solid 1px; background-color: #ffa94d33;">OPO Mode</span>
        {/if}
    </svelte:fragment>
    <svelte:fragment slot="buttonContainer">
        <InitFunctionRow
            {theoryLocation}
            {normMethod}
            bind:theoryRow
            {removeExtraFile}
            {felixfiles}
            {plotfile}
            class={felix_toggle ? '' : 'hide'}
            {showall}
        />
        <OPORow
            {normMethod}
            {showall}
            {removeExtraFile}
            bind:OPOLocation
            bind:OPOfilesChecked
            bind:opofiles
            {plotfile}
            class={opo_toggle ? '' : 'hide'}
        />
        <TheoryRow bind:theoryLocation {normMethod} class={theory_toggle ? '' : 'hide'} {theoryRow} />
        <div class="align" class:hide={!felix_toggle}>
            <CustomRadio bind:value={normMethod} options={normMethods} />
        </div>

        <div class="align">
            <div style="display: flex; gap: 0.5em;">
                <CustomSwitch bind:selected={showall} label="plot-all-files" />
                {#if !showall}
                    <CustomSelect bind:value={plotfile} label="plotfile" options={plotfileOptions} />
                {/if}
            </div>
            <CustomSegBtn class="ml-auto" bind:choices={show_graphs} />
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer">
        <div
            class="animate__animated animate__fadeIn graph__div"
            class:hide={!showTheory}
            id="{uniqueID}-exp-theory-plot"
        />
        <div id="{uniqueID}-felix_graphs" class:hide={!showFELIX}>
            <div id="{uniqueID}-bplot" class="graph__div" class:hide={!showRawData} />
            <div id="{uniqueID}-saPlot" class="graph__div" class:hide={!showPowerData} />
            <div
                id="{uniqueID}-avgplot"
                class="graph__div"
                on:plotted={(e) => {
                    if (e.detail.graphDiv === `${uniqueID}-avgplot`) {
                        graphPlotted = true
                    }
                }}
            />
        </div>

        <div id="{uniqueID}-opo_graphs" class:hide={!showOPO}>
            <div
                class="animate__animated animate__fadeIn graph__div"
                class:hide={!showRawData}
                id="{uniqueID}-opoplot"
            />
            <div class="animate__animated animate__fadeIn graph__div" class:hide={!showRawData} id="{uniqueID}-opoSA" />
            <div
                class="animate__animated animate__fadeIn graph__div"
                id="{uniqueID}-opoRelPlot"
                on:plotted={(e) => {
                    if (e.detail.graphDiv === `${uniqueID}-opoRelPlot`) {
                        graphPlotted = true
                    }
                }}
            />
        </div>
    </svelte:fragment>

    <svelte:fragment slot="config">
        <GetFileInfoTable {felixfiles} {opofiles} {normMethod} />
    </svelte:fragment>

    <svelte:fragment slot="plotContainer_functions">
        <WriteFunctionContents
            on:addfile={() => {
                addFileModal = true
            }}
            on:removefile={removeExtraFile}
            {output_namelists}
            bind:writeFileName
            bind:writeFile
            bind:overwrite_expfit
        />

        <ExecuteFunctionContents
            {normMethod}
            {showall}
            bind:modalActivate
            bind:adjustPeakTrigger
            {...{
                fullfiles,
                writeFile,
                addedFileCol,
                writeFileName,
                addedFileScale,
                overwrite_expfit,
            }}
        />
    </svelte:fragment>
    <svelte:fragment slot="plotContainer_reports">
        <FrequencyTable {normMethod} />
    </svelte:fragment>
</Layout>

<style lang="scss">
    .graph__div {
        margin-bottom: 1em;
    }
</style>
