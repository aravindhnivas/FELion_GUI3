<script lang="ts">
    import { opoMode, felixPlotAnnotations } from '../../functions/svelteWritables'
    import { felix_opo_func } from '../../functions/felix_opo_func'

    import plotIndividualDataIntoGraph, {
        get_data,
        mapNormMethodKeys,
    } from '../../functions/plotIndividualDataIntoGraph'

    import CustomSelect from '$components/CustomSelect.svelte'
    import QuickBrowser from '$components/QuickBrowser.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import { plot } from '$src/js/functions'
    import computePy_func from '$src/Pages/general/computePy'
    // import { react } from 'plotly.js-basic-dist'
    import BrowseTextfield from '$src/components/BrowseTextfield.svelte'
    import { plotlayout } from '../../functions/plot_labels'

    /////////////////////////////////////////////////////////////////////////

    export let plotfile
    export let opofiles
    export let OPOLocation
    export let removeExtraFile
    export let OPOfilesChecked
    export let showall = true
    export let normMethod: string

    let className = ''
    export { className as class }
    /////////////////////////////////////////////////////////////////////////

    let opoPower = 1
    let deltaOPO = 0.3

    const uniqueID = getContext<string>('uniqueID')
    let calibFile = ''
    let showOPOFiles = false
    let OPOcalibFiles = []

    $: if (window.fs.isDirectory(OPOLocation)) {
        OPOcalibFiles = window.fs.readdirSync(OPOLocation).filter((file) => file.endsWith('.calibOPO'))
        opofiles = OPOfilesChecked.map((file) => window.path.resolve(OPOLocation, file))
    }

    let dataReady = false
    const fullData = {}

    function plotData({ e = null, tkplot = 'run', general = false } = {}) {
        removeExtraFile()

        if (opofiles.length < 1) return window.createToast('No files selected', 'danger')
        $felixPlotAnnotations[uniqueID] = []

        const args = { opofiles, tkplot, $deltaOPO: deltaOPO, calibFile, opoPower }
        if (general)
            return computePy_func({
                e,
                pyfile: 'normline.oposcan',
                args,
                general,
            })

        dataReady = false

        computePy_func({ e, pyfile: 'normline.oposcan', args, general }).then((dataFromPython) => {
            fullData.data = dataFromPython
            dataReady = true
            // $opoMode[uniqueID] = true
            showOPOFiles = false
        })
    }

    $: updateplot = dataReady && plotfile && normMethod && fullData.data && $opoMode[uniqueID]
    $: if (updateplot && showall) {
        if (currentGraph.hasAttribute('data-plotted')) {
            // const currentKey = mapNormMethodKeys[normMethod]
            // const currentData = get_data(fullData.data[currentKey])
            // react(`${uniqueID}-opoRelPlot`, currentData, plotlayout[normMethod])
            const { yaxis, xaxis, title, key } = plotlayout[normMethod]
            plot(title, xaxis.title, yaxis.title, fullData.data[key], `${uniqueID}-opoRelPlot`)
            plot('Baseline Corrected', 'Wavelength (cm-1)', 'Counts', fullData.data['base'], `${uniqueID}-opoplot`)
            plot(
                'OPO Calibration',
                'Set Wavenumber (cm-1)',
                'Measured Wavenumber (cm-1)',
                fullData.data['SA'],
                `${uniqueID}-opoSA`
            )
        } else {
            felix_opo_func({ dataFromPython: fullData.data, uniqueID, mode: 'opo', normMethod })
        }
    } else if (updateplot) {
        plotIndividualDataIntoGraph({
            fullData,
            plotfile,
            uniqueID,
            normMethod,
        })
    }

    let currentGraph: HTMLElement

    onMount(() => {
        currentGraph = document.getElementById(`${uniqueID}-opoRelPlot`)
    })
</script>

<QuickBrowser
    title="OPO files"
    filetype="ofelix"
    bind:active={showOPOFiles}
    bind:currentLocation={OPOLocation}
    bind:fileChecked={OPOfilesChecked}
    on:submit={(e) => {
        plotData({ e: e.detail.event })
    }}
/>

{#if $opoMode[uniqueID]}
    <div class="align box p-2 {className}" style="background-color: #ffa94d33;">
        <BrowseTextfield class="p-1 two_col_browse" bind:value={OPOLocation} label="OPO location" />
        {#if window.fs.isDirectory(OPOLocation)}
            <div class="align">
                <button
                    class="button is-warning"
                    on:click={() => {
                        showOPOFiles = !showOPOFiles
                    }}
                >
                    Show files</button
                >
                <CustomSelect bind:value={calibFile} label="Calib. file" options={OPOcalibFiles} />
                <CustomTextSwitch
                    style="width:7em;"
                    step="0.1"
                    variant="outlined"
                    bind:value={deltaOPO}
                    label="Delta OPO"
                />
                <CustomTextSwitch
                    style="width:9em"
                    step="0.1"
                    variant="outlined"
                    bind:value={opoPower}
                    label="Power (mJ)"
                />
                <button class="button is-link" on:click={(e) => plotData({ e })}>Replot</button>
            </div>
        {/if}
    </div>
{/if}
