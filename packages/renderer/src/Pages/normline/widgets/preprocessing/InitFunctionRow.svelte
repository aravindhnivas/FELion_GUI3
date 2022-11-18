<script lang="ts">
    import {
        opoMode,
        normMethod,
        felixPeakTable,
        expfittedLines,
        normMethodDatas,
        felixOutputName,
        fittedTraceCount,
        felixopoLocation,
        felixPlotCheckboxes,
        felixPlotAnnotations,
        expfittedLinesCollectedData,
        theoryLocation,
    } from '../../functions/svelteWritables'
    import FelixPlotting from '../../modals/FelixPlotting.svelte'
    import { felix_opo_func } from '../../functions/felix_opo_func'
    import plotIndividualDataIntoGraph, {
        get_data,
        mapNormMethodKeys,
    } from '../../functions/plotIndividualDataIntoGraph'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import { subplot, plot } from '$src/js/functions'
    import computePy_func from '$src/Pages/general/computePy'
    import { react, relayout } from 'plotly.js-basic-dist'
    import ButtonBadge from '$components/ButtonBadge.svelte'
    ///////////////////////////////////////////////////////////////////////////

    export let plotfile = 'average'
    export let felixfiles = []
    export let removeExtraFile
    export let showall = true
    export let theoryRow = false

    let className = ''
    export { className as class }
    ///////////////////////////////////////////////////////////////////////////

    const uniqueID = getContext<string>('uniqueID')

    let active = false
    let deltaFELIX = 1
    let felixPlotWidgets = {
        text: [
            {
                label: 'Exp_title',
                value: 'FELIX-Experiment',
                id: window.getID(),
            },
            { label: 'Exp_legend', value: 'legend', id: window.getID() },
            { label: 'Cal_title', value: 'calc_title', id: window.getID() },
        ],

        number: [
            { label: 'freqScale', value: '1', id: window.getID() },
            { label: 'theorySigma', value: '5', id: window.getID() },
        ],
        boolean: [{ label: 'Only_exp', value: true, id: window.getID() }],
    }

    const fullData = {}
    let dataReady = false

    async function plotData({ e = null, filetype = 'felix', target = null } = {}) {
        let pyfile = ''
        let args

        switch (filetype) {
            case 'felix':
                if (felixfiles.length < 1) return window.createToast('No files selected', 'danger')

                removeExtraFile()

                if (document.getElementById(`${uniqueID}-avgplot`)?.data) {
                    relayout(`${uniqueID}-avgplot`, {
                        annotations: [],
                        shapes: [],
                        line: [],
                    })
                }
                dataReady = false

                pyfile = 'normline.felix'
                args = { felixfiles, $deltaFELIX: deltaFELIX }

                $felixPeakTable = []
                // $felixPlotAnnotations = []
                $felixPlotAnnotations[uniqueID] = []
                $felixOutputName = 'averaged'

                const dataFromPython = await computePy_func({
                    e,
                    target,
                    pyfile,
                    args,
                })
                if (!dataFromPython) return

                $expfittedLines = []
                $fittedTraceCount = 0
                // $felixPlotAnnotations = []
                $felixPlotAnnotations[uniqueID] = []
                $expfittedLinesCollectedData = []

                fullData.data = dataFromPython
                dataReady = true
                break

            case 'baseline':
                const filebrowserID = `#${uniqueID}-${$opoMode ? 'o' : ''}felix_filebrowser`
                const baseline_markedfile = document.querySelector(`${filebrowserID} .marked-file`)?.textContent
                console.log(baseline_markedfile)
                if (!baseline_markedfile) {
                    return window.createToast(
                        `No ${
                            $opoMode ? 'OPO' : 'FELIX'
                        } files: ctrl + left-click to select file for baseline correction`,
                        'danger'
                    )
                }

                pyfile = 'normline.baseline'
                args = {
                    filename: window.path.join($felixopoLocation, baseline_markedfile),
                }
                computePy_func({ e, pyfile, args, general: true })
                break

            case 'matplotlib':
                const numberWidgets: { [name: string]: number } = {}
                felixPlotWidgets.number.forEach((n) => (numberWidgets[n.label] = parseFloat(n.value)))

                const textWidgets = {}
                felixPlotWidgets.text.forEach((n) => (textWidgets[n.label] = n.value))
                const booleanWidgets = {}
                felixPlotWidgets.boolean.forEach((n) => (booleanWidgets[n.label] = n.value))
                const selectedWidgets = {}
                $felixPlotCheckboxes.forEach((n) => (selectedWidgets[n.label] = n.value))

                pyfile = 'normline.felix_tkplot'
                args = {
                    numberWidgets,
                    textWidgets,
                    booleanWidgets,
                    selectedWidgets,
                    location: $felixopoLocation,
                    normMethod: $normMethod,
                    theoryLocation: $theoryLocation,
                }

                computePy_func({ e, pyfile, args, general: true })
            default:
                break
        }
    }

    $: updateplot = !$opoMode && dataReady && plotfile && $normMethod && fullData.data

    $: if (updateplot && showall) {
        if (currentGraph.hasAttribute('data-plotted')) {
            const currentKey = mapNormMethodKeys[$normMethod]
            const currentData = get_data(fullData.data[currentKey])
            const { layout } = $normMethodDatas[$normMethod]
            console.warn('plotting', currentData, layout)

            plot('Baseline Corrected', 'Wavelength (cm-1)', 'Counts', fullData.data['base'], `${uniqueID}-bplot`)
            subplot(
                'Spectrum and Power Analyser',
                'Wavelength set (cm-1)',
                'SA (cm-1)',
                fullData.data['SA'],
                `${uniqueID}-saPlot`,
                'Wavelength (cm-1)',
                `Total Power (mJ)`,
                fullData.data['pow']
            )
            react(`${uniqueID}-avgplot`, currentData, layout)
        } else {
            felix_opo_func({ dataFromPython: fullData.data, uniqueID, mode: 'felix' })
        }
    } else if (updateplot) {
        plotIndividualDataIntoGraph({
            fullData,
            plotfile,
            uniqueID,
        })
    }

    let currentGraph: HTMLElement
    onMount(() => {
        currentGraph = document.getElementById(`${uniqueID}-avgplot`)
    })
</script>

<FelixPlotting
    bind:active
    bind:felixPlotWidgets
    on:submit={(e) => plotData({ e: e.detail.event, filetype: 'matplotlib' })}
/>

<div class="align {className}">
    <ButtonBadge
        id="create_baseline_btn"
        on:click={(e) => plotData({ e: e, filetype: 'baseline' })}
        label="Create Baseline"
    />

    <button class="button is-link" id="felix_plotting_btn" on:click={(e) => plotData({ e: e, filetype: 'felix' })}>
        FELIX Plot
    </button>

    <CustomTextSwitch style="width:7em" variant="outlined" bind:value={deltaFELIX} label="Delta" step="0.5" />
    <button class="button is-link" on:click={() => (active = true)}> Open in Matplotlib</button>
    <button class="button is-link" on:click={() => (theoryRow = !theoryRow)}>Add Theory</button>
    <button
        class="button is-link"
        on:click={() => {
            $opoMode = !$opoMode
        }}>OPO</button
    >
</div>
