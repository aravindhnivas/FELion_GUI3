<script lang="ts">
    import {
        felixIndex,
        // normMethod,
        opoMode,
        dataTable,
        expfittedLines,
        felixPeakTable,
        felixOutputName,
        felixopoLocation,
        felixPlotAnnotations,
        felixAnnotationColor,
        expfittedLinesCollectedData,
    } from '../../functions/svelteWritables'
    // import Textfield from '@smui/textfield'
    import { savefile, loadfile } from '../../functions/misc'
    import { NGauss_fit_func } from '../../functions/NGauss_fit'
    import { exp_fit_func } from '../../functions/exp_fit'
    import { relayout, deleteTraces } from 'plotly.js-basic-dist'
    import { dropRight, sortBy } from 'lodash-es'
    import computePy_func from '$src/Pages/general/computePy'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'
    // //////////////////////////////////////////////////////////////////////

    export let writeFile: boolean = false
    export let normMethod: string
    export let showall = true
    export let fullfiles
    export let addedFileCol
    export let writeFileName
    export let addedFileScale
    export let overwrite_expfit
    export let modalActivate = false
    export let adjustPeakTrigger = false

    // //////////////////////////////////////////////////////////////////////
    const uniqueID = getContext<string>('uniqueID')
    let NGauss_fit_args: { fitNGauss_arguments: { [name: string]: number }; index: [] } = {
        fitNGauss_arguments: {},
        index: [],
    }
    let savePeakfilename = 'peakTable'
    let toggleFindPeaksRow = false
    let boxSelected_peakfinder = false
    let fitall = false

    $: currentGraph = $opoMode ? `${uniqueID}-opoRelPlot` : `${uniqueID}-avgplot`

    const clearAllPeak = () => {
        const graphElement = document.getElementById(currentGraph)

        relayout(currentGraph, { annotations: [], shapes: [], line: [] })

        const defaultLength = showall ? fullfiles.length : 1
        const noOfFittedData = graphElement.data?.length - defaultLength
        if (noOfFittedData === 0) {
            return window.createToast('No fitted lines found', 'danger')
        }

        console.log('Removing all found peak values')
        console.log({ noOfFittedData }, fullfiles.length, graphElement.data?.length)

        $felixIndex[uniqueID] = []
        $felixPlotAnnotations[uniqueID] = []
        $expfittedLines = []
        $expfittedLinesCollectedData = []
        relayout(currentGraph, { annotations: [], shapes: [] })

        for (let i = 0; i < noOfFittedData; i++) {
            deleteTraces(currentGraph, [-1])
        }
    }

    const clearLastPeak = () => {
        const graphElement = document.getElementById(currentGraph)
        const defaultLength = showall ? fullfiles.length : 1
        const noOfFittedData = graphElement.data?.length - defaultLength
        if (noOfFittedData === 0) {
            return window.createToast('No fitted lines found', 'danger')
        }
        $dataTable[uniqueID] = dropRight($dataTable[uniqueID], 1)
        $expfittedLines = dropRight($expfittedLines, 2)

        $felixPlotAnnotations[uniqueID] = dropRight($felixPlotAnnotations[uniqueID], 1)
        $expfittedLinesCollectedData = dropRight($expfittedLinesCollectedData, 1)
        relayout(currentGraph, {
            annotations: $felixPlotAnnotations[uniqueID],
            shapes: $expfittedLines,
        })

        deleteTraces(currentGraph, [-1])
        window.createToast('Last fitted peak removed', 'warning')
    }

    function loadpeakTable() {
        const loadedfile = loadfile(savePeakfilename, $felixopoLocation)
        if (loadedfile.length < 1) return
        $felixPeakTable[uniqueID] = sortBy(loadedfile, [(o) => o['freq']])
        adjustPeak()
    }

    function adjustPeak() {
        const annotationDefaults = {
            xref: 'x',
            y: 'y',
            showarrow: true,
            arrowhead: 2,
            ax: -25,
            ay: -40,
            font: { color: $felixAnnotationColor },
            arrowcolor: $felixAnnotationColor,
        }

        $felixPlotAnnotations[uniqueID] = $felixPeakTable[uniqueID].map((f) => {
            const { freq, amp } = f
            // const x = parseFloat(freq)
            // const y = parseFloat(amp)
            const annotate = {
                x: freq,
                y: amp,
                text: `(${freq.toFixed(2)}, ${amp.toFixed(2)})`,
            }
            return { ...annotationDefaults, ...annotate }
        })

        modalActivate = false
        relayout(currentGraph, { annotations: $felixPlotAnnotations[uniqueID] })
        adjustPeakTrigger = false
    }

    function plotData({ e = null, filetype = 'exp_fit', general = { pyfile: '', args: '' } } = {}) {
        if (filetype == 'general') {
            const { pyfile, args } = general
            computePy_func({ pyfile, args, general: true })
            return
        }

        switch (filetype) {
            case 'exp_fit':
                if (!$felixOutputName[uniqueID]) {
                    return window.createToast('Output name not found!!. Please select output filename', 'danger')
                }
                if ($felixIndex[uniqueID].length < 2) {
                    return window.createToast('Range not found!!. Select a range using Box-select', 'danger')
                }

                const expfit_args = {
                    fullfiles,
                    writeFile,
                    addedFileCol,
                    writeFileName,
                    addedFileScale,
                    overwrite_expfit,
                    normMethod,
                    index: $felixIndex[uniqueID],
                    location: $felixopoLocation,
                    output_name: $felixOutputName[uniqueID],
                }
                computePy_func({
                    e,
                    pyfile: 'normline.exp_gauss_fit',
                    args: expfit_args,
                }).then((dataFromPython) => {
                    exp_fit_func({ dataFromPython, uniqueID })
                    // window.createToast("Line fitted with gaussian function", "success")
                })
                break

            case 'NGauss_fit':
                if (!$felixOutputName[uniqueID]) {
                    return window.createToast('Output name not found!!. Please select output filename', 'danger')
                }
                if (boxSelected_peakfinder) {
                    if ($felixIndex[uniqueID].length < 2) {
                        window.createToast('Box selection is turned ON so please select a wn. range to fit', 'danger')
                        return
                    }

                    NGauss_fit_args.index = $felixIndex[uniqueID]
                } else {
                    NGauss_fit_args.index = []
                }

                if ($felixPeakTable[uniqueID].length === 0) {
                    return window.createToast('No arguments initialised yet.', 'danger')
                }

                NGauss_fit_args.fitNGauss_arguments = {}

                $felixPeakTable[uniqueID].forEach((f, index) => {
                    NGauss_fit_args.fitNGauss_arguments[`cen${index}`] = f.freq
                    NGauss_fit_args.fitNGauss_arguments[`A${index}`] = f.amp
                    NGauss_fit_args.fitNGauss_arguments[`sigma${index}`] = f.sig
                })
                NGauss_fit_args = {
                    ...NGauss_fit_args,
                    location: $felixopoLocation,
                    addedFileScale,
                    addedFileCol,
                    overwrite_expfit,
                    writeFile,
                    writeFileName,
                    output_name: $felixOutputName[uniqueID],
                    fullfiles,
                    fitall,
                    normMethod,
                }

                computePy_func({
                    e,
                    pyfile: 'normline.multiGauss',
                    args: NGauss_fit_args,
                }).then((dataFromPython) => {
                    NGauss_fit_func({ dataFromPython, uniqueID })
                    if (dataFromPython[normMethod]) {
                        console.log('Line fitted')
                        window.createToast(
                            `Line fitted with ${dataFromPython[normMethod]['fitted_parameter'].length} gaussian function`,
                            'success'
                        )
                    }
                })

                break

            default:
                break
        }
    }
    $: if (adjustPeakTrigger) adjustPeak()
    onMount(() => {
        felixIndex.init(uniqueID)
        felixPeakTable.init(uniqueID)
        felixOutputName.init(uniqueID)
        felixPlotAnnotations.init(uniqueID)
        return () => {
            felixIndex.remove(uniqueID)
            felixPeakTable.remove(uniqueID)
            felixOutputName.remove(uniqueID)
            felixPlotAnnotations.remove(uniqueID)
        }
    })
</script>

<div class="align">
    <button class="button is-link" on:click={(e) => plotData({ e: e, filetype: 'exp_fit' })}>Exp Fit.</button>
    <button class="button is-link" on:click={() => (toggleFindPeaksRow = !toggleFindPeaksRow)}>Fit NGauss.</button>
    <button class="button is-warning" on:click={clearLastPeak}>Clear Last</button>
    <button class="button is-danger" on:click={clearAllPeak}>Clear All</button>
</div>

{#if toggleFindPeaksRow}
    <div class="align v-baseline">
        <div class="align">
            <i role="presentation" class="material-symbols-outlined" on:click={() => (modalActivate = true)}>settings</i
            >
            <CustomSwitch bind:selected={boxSelected_peakfinder} label="limited range" />
            <CustomSwitch bind:selected={fitall} label="fit all methods" />
            <button
                style="width:7em"
                class="button is-link"
                on:click={(e) => plotData({ e: e, filetype: 'NGauss_fit' })}
            >
                Fit
            </button>

            <TextAndSelectOptsToggler
                bind:value={savePeakfilename}
                label="savefile"
                lookIn={$felixopoLocation}
                lookFor=".json"
                auto_init={true}
            />

            <button
                class="button is-link"
                on:click={() =>
                    savefile({ file: $felixPeakTable[uniqueID], name: savePeakfilename, location: $felixopoLocation })}
            >
                Save peaks
            </button>
            <button class="button is-link" on:click={loadpeakTable}>Load peaks</button>
            <button
                class="button is-danger"
                on:click={() => {
                    $felixPlotAnnotations[uniqueID] = []
                    $felixPeakTable[uniqueID] = []
                    NGauss_fit_args = { fitNGauss_arguments: {}, index: [] }
                    relayout(currentGraph, { annotations: [] })
                    window.createToast('Cleared', 'warning')
                }}
            >
                Clear
            </button>
        </div>
    </div>
{/if}
