<script>
    import {
        opoMode,
        showall,
        toggleRow,
        normMethod,
        baselineFile,
        felixPeakTable,
        expfittedLines,
        normMethodDatas,
        felixOutputName,
        fittedTraceCount,
        felixopoLocation,
        felixGraphPlotted,
        felixPlotCheckboxes,
        felixPlotAnnotations,
        expfittedLinesCollectedData,
    } from '../../functions/svelteWritables'
    import FelixPlotting from '../../modals/FelixPlotting.svelte'
    import { felix_func } from '../../functions/felix'
    import plotIndividualDataIntoGraph, {
        get_data,
        mapNormMethodKeys,
    } from '../../functions/plotIndividualDataIntoGraph'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import { subplot, plot } from '$src/js/functions.js'
    import computePy_func from '$src/Pages/general/computePy'
    import { react, relayout } from 'plotly.js/dist/plotly-basic'

    ///////////////////////////////////////////////////////////////////////////

    export let plotfile = 'average'
    export let felixfiles = []
    export let theoryLocation = ''
    export let removeExtraFile
    ///////////////////////////////////////////////////////////////////////////

    let delta = 1
    let active = false
    let openShell = false

    let felixPlotWidgets = {
        text: [
            { label: 'Exp_title', value: 'FELIX-Experiment', id: getID() },
            { label: 'Exp_legend', value: 'legend', id: getID() },
            { label: 'Cal_title', value: 'calc_title', id: getID() },
        ],

        number: [
            { label: 'freqScale', value: 1, step: 0.01, id: getID() },
            { label: 'theorySigma', value: 5, step: 1, id: getID() },
        ],
        boolean: [{ label: 'Only_exp', value: true, id: getID() }],
    }

    const fullData = {}
    let dataReady = false
    async function plotData({
        e = null,
        filetype = 'felix',
        target = null,
    } = {}) {
        let pyfile = '',
            args

        switch (filetype) {
            case 'felix':
                if (felixfiles.length < 1)
                    return window.createToast('No files selected', 'danger')

                removeExtraFile()

                if (document.getElementById('avgplot')?.data) {
                    relayout('avgplot', {
                        annotations: [],
                        shapes: [],
                        line: [],
                    })
                }
                dataReady = false

                pyfile = 'normline.felix'
                args = { felixfiles, delta }

                $felixPeakTable = []
                $felixPlotAnnotations = []
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
                $felixPlotAnnotations = []
                $expfittedLinesCollectedData = []

                fullData.data = dataFromPython
                dataReady = true

                break

            case 'baseline':
                const baseline_markedfile = document.querySelector(
                    `#${$opoMode ? 'o' : ''}felix_filebrowser .marked-file`
                )?.textContent

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
                    filename: pathJoin($felixopoLocation, baseline_markedfile),
                }
                computePy_func({ e, pyfile, args, general: true })
                break

            case 'matplotlib':
                const numberWidgets = {}
                felixPlotWidgets.number.forEach(
                    (n) => (numberWidgets[n.label] = n.value)
                )

                const textWidgets = {}
                felixPlotWidgets.text.forEach(
                    (n) => (textWidgets[n.label] = n.value)
                )
                const booleanWidgets = {}
                felixPlotWidgets.boolean.forEach(
                    (n) => (booleanWidgets[n.label] = n.value)
                )
                const selectedWidgets = {}
                $felixPlotCheckboxes.forEach(
                    (n) => (selectedWidgets[n.label] = n.value)
                )

                pyfile = 'normline.felix_tkplot'
                args = {
                    numberWidgets,
                    textWidgets,
                    booleanWidgets,
                    selectedWidgets,
                    location: $felixopoLocation,
                    normMethod: $normMethod,
                    theoryLocation,
                }

                computePy_func({ e, pyfile, args, general: true })
            default:
                break
        }
    }

    $: updateplot =
        dataReady && plotfile && $normMethod && fullData.data && !$opoMode
    $: if (updateplot && $showall) {
        if ($felixGraphPlotted) {
            const currentKey = mapNormMethodKeys[$normMethod]
            const currentData = get_data(fullData.data[currentKey])

            const { layout } = $normMethodDatas[$normMethod]
            react('avgplot', currentData, layout)
            plot(
                'Baseline Corrected',
                'Wavelength (cm-1)',
                'Counts',
                fullData.data['base'],
                'bplot'
            )
            subplot(
                'Spectrum and Power Analyser',
                'Wavelength set (cm-1)',
                'SA (cm-1)',
                fullData.data['SA'],
                'saPlot',
                'Wavelength (cm-1)',
                `Total Power (mJ)`,
                fullData.data['pow']
            )
        } else {
            felix_func({ dataFromPython: fullData.data, delta })
        }
    } else if (updateplot) {
        plotIndividualDataIntoGraph({
            fullData,
            plotfile,
            graphPlotted: $felixGraphPlotted,
            delta,
        })
    }
</script>

<FelixPlotting
    bind:active
    bind:felixPlotWidgets
    {theoryLocation}
    on:submit={(e) => plotData({ e: e.detail.event, filetype: 'matplotlib' })}
/>

<div class="align">
    <button
        class="button is-link"
        id="create_baseline_btn"
        on:click={(e) => plotData({ e: e, filetype: 'baseline' })}
    >
        Create Baseline
        <span
            class="tag__span tag is-warning "
            aria-label="ctrl + left-click to select file for baseline correction"
            data-cooltipz-dir="bottom">b</span
        >
    </button>

    <button
        class="button is-link"
        id="felix_plotting_btn"
        on:click={(e) => plotData({ e: e, filetype: 'felix' })}
    >
        FELIX Plot
    </button>

    <CustomTextSwitch
        style="width:7em"
        variant="outlined"
        bind:value={delta}
        label="Delta"
        step="0.5"
    />
    <button class="button is-link" on:click={() => (active = true)}>
        Open in Matplotlib</button
    >
    <button class="button is-link" on:click={() => ($toggleRow = !$toggleRow)}
        >Add Theory</button
    >
    <button
        class="button is-link"
        on:click={() => {
            $opoMode = !$opoMode
        }}>OPO</button
    >
</div>
