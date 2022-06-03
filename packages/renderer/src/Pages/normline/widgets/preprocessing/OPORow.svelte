<script>
    import {
        showall,
        opoMode,
        normMethod,
        baselineFile,
        OPOGraphPlotted,
        normMethodDatas,
        felixPlotAnnotations,
    } from '../../functions/svelteWritables'
    import { opofile_func } from '../../functions/opofile'

    import plotIndividualDataIntoGraph, {
        get_data,
        mapNormMethodKeys,
    } from '../../functions/plotIndividualDataIntoGraph'

    import CustomSelect from '$components/CustomSelect.svelte'
    import QuickBrowser from '$components/QuickBrowser.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import { plot } from '$src/js/functions'
    import computePy_func from '$src/Pages/general/computePy'
    import { react } from 'plotly.js/dist/plotly-basic'

    /////////////////////////////////////////////////////////////////////////

    export let plotfile
    export let opofiles
    export let OPOLocation
    export let removeExtraFile
    export let OPOfilesChecked

    /////////////////////////////////////////////////////////////////////////

    let opoPower = 1
    let deltaOPO = 0.3
    let calibFile = ''
    let showOPOFiles = false
    let OPOcalibFiles = []

    $: if (window.fs.existsSync(OPOLocation)) {
        OPOcalibFiles = window.fs.readdirSync(OPOLocation).filter((file) => file.endsWith('.calibOPO'))
        opofiles = OPOfilesChecked.map((file) => window.path.resolve(OPOLocation, file))
    }

    let dataReady = false
    const fullData = {}

    function plotData({ e = null, tkplot = 'run', general = false } = {}) {
        removeExtraFile()

        if (opofiles.length < 1) return window.createToast('No files selected', 'danger')
        ;($opoMode = true), ($felixPlotAnnotations = [])

        // const general = tkplot==="plot"

        const args = { opofiles, tkplot, deltaOPO, calibFile, opoPower }
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
            $opoMode = true
            showOPOFiles = false
        })
    }

    $: updateplot = dataReady && plotfile && $normMethod && fullData.data && $opoMode
    $: if (updateplot && $showall) {
        if ($OPOGraphPlotted) {
            const currentKey = mapNormMethodKeys[$normMethod]
            const currentData = get_data(fullData.data[currentKey])
            const { layout } = $normMethodDatas[$normMethod]
            react('opoRelPlot', currentData, layout)
            plot('Baseline Corrected', 'Wavelength (cm-1)', 'Counts', fullData.data['base'], 'opoplot')
            plot('OPO Calibration', 'Set Wavenumber (cm-1)', 'Measured Wavenumber (cm-1)', fullData.data['SA'], 'opoSA')
        } else {
            opofile_func({ dataFromPython: fullData.data, delta: deltaOPO })
            $OPOGraphPlotted = true
        }
    } else if (updateplot) {
        console.log({ $showall, plotfile })
        plotIndividualDataIntoGraph({
            fullData,
            plotfile,
            graphPlotted: $OPOGraphPlotted,
            delta: deltaOPO,
        })
    }
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
    on:markedFile={(e) => ($baselineFile = e.detail.markedFile)}
/>

{#if $opoMode}
    <div class="align">
        <span class="tag is-warning ">OPO Mode: </span>
        <button
            class="button is-link"
            on:click={() => {
                showOPOFiles = !showOPOFiles
            }}
        >
            Browse File</button
        >
        <CustomSelect bind:value={calibFile} label="Calib. file" options={OPOcalibFiles} />
        <CustomTextSwitch style="width:7em;" step="0.1" variant="outlined" bind:value={deltaOPO} label="Delta OPO" />
        <CustomTextSwitch style="width:9em" step="0.1" variant="outlined" bind:value={opoPower} label="Power (mJ)" />
        <button class="button is-link" on:click={(e) => plotData({ e })}>Replot</button>
        <button class="button is-link" on:click={(e) => plotData({ e, tkplot: 'plot', general: true })}
            >Open in Matplotlib</button
        >
    </div>
{/if}
