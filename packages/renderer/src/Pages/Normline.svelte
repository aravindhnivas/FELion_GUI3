<script>
    import {
        showall,
        opoMode,
        graphDiv,
        normMethod,
        normMethods,
        showRawData,
        baselineFile,
        Ngauss_sigma,
        showPowerData,
        felixopoLocation,
        OPOGraphPlotted,
        felixGraphPlotted,
    } from './normline/functions/svelteWritables'

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
    // import IconButton from '$components/IconButton.svelte'
    import Layout from '$components/Layout.svelte'
    import CustomRadio from '$components/CustomRadio.svelte'
    import { deleteTraces } from 'plotly.js-basic-dist'
    import { onDestroy } from 'svelte'
    ///////////////////////////////////////////////////////////////////////

    const filetype = 'felix'
    const id = 'Normline'

    let fileChecked = []
    // let toggleBrowser = false;
    let currentLocation = ''

    $: felixfiles = fileChecked.map((file) => window.path.resolve(currentLocation, file))
    $: console.log(`${filetype} currentlocation: \n${currentLocation}`)

    ///////////////////////////////////////////////////////////////////////
    // Theory file

    let showTheory = true
    let theoryLocation = window.db.get('theoryLocation') || currentLocation

    $: graphPlotted = $felixGraphPlotted || $OPOGraphPlotted
    $: console.log({ graphPlotted, $OPOGraphPlotted, $felixGraphPlotted })
    let overwrite_expfit = true
    let writeFile = true
    let OPOfilesChecked = []
    let writeFileName = 'average_normline.dat'
    let keepTable = true

    $: plottedFiles = $opoMode
        ? OPOfilesChecked.map((file) => file.split('.')[0]) || []
        : fileChecked.map((file) => file.split('.')[0]) || []
    $: output_namelists = [
        'averaged',
        ...plottedFiles,
        ...addedfiles.map((file) => window.path.basename(file)).map((file) => file.split('.')[0]),
    ]

    // OPO
    let OPOLocation = window.db.get('ofelix_location') || currentLocation
    let opofiles = []

    $: $felixopoLocation = $opoMode ? OPOLocation : currentLocation
    // $: $opoMode ? window.createToast("OPO MODE") : window.createToast("FELIX MODE")
    $: $Ngauss_sigma = $opoMode ? 2 : 5

    let addFileModal = false
    let addedFile = {}
    let addedfiles = []
    let addedFileCol = '0, 1'
    let addedFileScale = 1
    let extrafileAdded = 0

    $: console.log(`Extrafile added: ${extrafileAdded}`)

    function removeExtraFile() {
        for (let i = 0; i < extrafileAdded + 1; i++) {
            try {
                deleteTraces($graphDiv, [-1])

                extrafileAdded--
                addedfiles = addedfiles.slice(0, addedfiles.length - 1)
            } catch (err) {
                console.log('The plot is empty')
            }
        }
    }

    $: fullfiles = $opoMode
        ? [...opofiles, ...addedfiles, window.path.resolve(currentLocation, 'averaged.felix')]
        : [...felixfiles, ...addedfiles, window.path.resolve(currentLocation, 'averaged.felix')]

    let activateConfigModal = false
    let modalActivate = false
    let adjustPeakTrigger = false
    // $: console.warn({ $opoMode })
    let plotfile = 'average'
    let showFELIX = true
    let showOPO = true
    let showMoreOptions = false
    $: plotfileOptions = $opoMode ? [...OPOfilesChecked, 'average'] : [...fileChecked, 'average']

    onDestroy(() => {
        $felixGraphPlotted = false
        $OPOGraphPlotted = false
    })

    let display = window.db.get('active_tab') === id ? 'block' : 'none'
</script>

<!-- Modals -->
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

<Layout
    {id}
    {display}
    {filetype}
    {graphPlotted}
    bind:fileChecked
    bind:currentLocation
    bind:activateConfigModal
    on:markedFile={(e) => ($baselineFile = e.detail.markedFile)}
>
    <svelte:fragment slot="buttonContainer">
        <InitFunctionRow {removeExtraFile} {felixfiles} {theoryLocation} {plotfile} />
        <OPORow {removeExtraFile} bind:OPOLocation bind:OPOfilesChecked bind:opofiles {plotfile} />
        <TheoryRow bind:theoryLocation />
        <div class="align">
            <CustomRadio bind:value={$normMethod} options={normMethods} />
            <button
                class="button is-link"
                style="margin-left: auto;"
                on:click={() => (showMoreOptions = !showMoreOptions)}
            >
                More options
                <i class=" material-symbols-outlined">{showMoreOptions ? 'arrow_drop_up' : 'arrow_drop_down'}</i>
            </button>
        </div>

        <div class="align" class:hide={!showMoreOptions}>
            <CustomSelect bind:value={plotfile} label="plotfile" options={plotfileOptions} />
            <CustomSwitch bind:selected={showFELIX} label="showFELIX" />
            <CustomSwitch bind:selected={showOPO} label="showOPO" />
            <CustomSwitch bind:selected={showTheory} label="showTheory" />
            <CustomSwitch bind:selected={$showall} label="showall" />
            <CustomSwitch bind:selected={$showRawData} label="showRawData" />
            <CustomSwitch bind:selected={$showPowerData} label="showPowerData" />
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer">
        <div class="animate__animated animate__fadeIn graph__div" class:hide={!showTheory} id="exp-theory-plot" />
        <div id="felix_graphs" class:hide={!showFELIX}>
            <div id="bplot" class="graph__div" class:hide={!$showRawData} />
            <div id="saPlot" class="graph__div" class:hide={!$showPowerData} />
            <div id="avgplot" class="graph__div" />
        </div>

        <div id="opo_graphs" class:hide={!showOPO}>
            <div class="animate__animated animate__fadeIn graph__div" class:hide={!$showRawData} id="opoplot" />
            <div class="animate__animated animate__fadeIn graph__div" class:hide={!$showRawData} id="opoSA" />
            <div class="animate__animated animate__fadeIn graph__div" id="opoRelPlot" />
        </div>
    </svelte:fragment>

    <svelte:fragment slot="config">
        <GetFileInfoTable {felixfiles} />
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
        <FrequencyTable bind:keepTable />
    </svelte:fragment>
</Layout>

<style>
    .graph__div {
        margin-bottom: 1em;
    }
</style>
