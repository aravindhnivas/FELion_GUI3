<script lang="ts">
    import {
        opoMode,
        // normMethod,
        normMethods,
        Ngauss_sigma,
        felixopoLocation,
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
    import Layout from '$components/Layout.svelte'
    import CustomRadio from '$components/CustomRadio.svelte'
    import { deleteTraces } from 'plotly.js-basic-dist'

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
    let keepTable = true

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

    $: $felixopoLocation[uniqueID] = $opoMode[uniqueID] ? OPOLocation : currentLocation
    // $: $opoMode ? window.createToast("OPO MODE") : window.createToast("FELIX MODE")
    $: $Ngauss_sigma = $opoMode[uniqueID] ? 2 : 5

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

    let showFELIX = true
    let showOPO = true
    let showMoreOptions = false

    $: plotfileOptions = $opoMode[uniqueID] ? [...OPOfilesChecked, 'average'] : [...fileChecked, 'average']

    onMount(() => {
        felixopoLocation.init(uniqueID)
        console.warn('Normline mounted')
    })
    onDestroy(() => {
        felixopoLocation.remove(uniqueID)
        console.warn('Normline destroyed')
    })

    let felix_toggle = true
    let opo_toggle = true
    let theory_toggle = true

    let showall = true
    let showRawData = true
    let showPowerData = true
    let normMethod: string = normMethods[1]
    let theoryRow = false
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

<Layout {id} {display} {filetype} {graphPlotted} bind:fileChecked bind:currentLocation bind:activateConfigModal>
    <svelte:fragment slot="toggle_row">
        {#if $opoMode[uniqueID]}
            <span class="tag" style="border: solid 1px; background-color: #ffa94d33;">OPO Mode</span>
        {/if}
    </svelte:fragment>
    <svelte:fragment slot="buttonContainer">
        <InitFunctionRow
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
        <TheoryRow {normMethod} class={theory_toggle ? '' : 'hide'} {theoryRow} />
        <div class="align" class:hide={!felix_toggle}>
            <CustomRadio bind:value={normMethod} options={normMethods} />
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
            <CustomSwitch bind:selected={showall} label="showall" />
            <CustomSwitch bind:selected={showRawData} label="showRawData" />
            <CustomSwitch bind:selected={showPowerData} label="showPowerData" />
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
