<script>
    import {
        felixIndex,
        normMethod,
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

    export let writeFile
    export let showall = true
    export let fullfiles
    export let addedFileCol
    export let writeFileName
    export let addedFileScale
    export let overwrite_expfit
    export let modalActivate = false
    export let adjustPeakTrigger = false

    // //////////////////////////////////////////////////////////////////////
    const uniqueID = getContext('uniqueID')
    let NGauss_fit_args = {}
    let savePeakfilename = 'peakTable'
    let toggleFindPeaksRow = false
    let boxSelected_peakfinder = false
    let fitall = true

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

        $felixIndex = []
        $expfittedLines = []
        $felixPlotAnnotations = []
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
        $dataTable = dropRight($dataTable, 1)
        $expfittedLines = dropRight($expfittedLines, 2)

        $felixPlotAnnotations = dropRight($felixPlotAnnotations, 1)
        $expfittedLinesCollectedData = dropRight($expfittedLinesCollectedData, 1)
        relayout(currentGraph, {
            annotations: $felixPlotAnnotations,
            shapes: $expfittedLines,
        })

        deleteTraces(currentGraph, [-1])
        window.createToast('Last fitted peak removed', 'warning')
    }

    function loadpeakTable() {
        const loadedfile = loadfile(savePeakfilename)
        if (loadedfile.length < 1) return
        $felixPeakTable = sortBy(loadedfile, [(o) => o['freq']])
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

        $felixPlotAnnotations = $felixPeakTable.map((f) => {
            const { freq, amp } = f
            const x = parseFloat(freq)
            const y = parseFloat(amp)
            const annotate = {
                x,
                y,
                text: `(${x.toFixed(2)}, ${y.toFixed(2)})`,
            }
            return { ...annotationDefaults, ...annotate }
        })

        modalActivate = false
        relayout(currentGraph, { annotations: $felixPlotAnnotations })
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
                if ($felixIndex.length < 2) {
                    return window.createToast('Range not found!!. Select a range using Box-select', 'danger')
                }

                const expfit_args = {
                    fullfiles,
                    writeFile,
                    addedFileCol,
                    writeFileName,
                    addedFileScale,
                    overwrite_expfit,
                    normMethod: $normMethod,
                    index: $felixIndex,
                    location: $felixopoLocation,
                    output_name: $felixOutputName,
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
                if (boxSelected_peakfinder) {
                    if ($felixIndex.length < 2) {
                        window.createToast('Box selection is turned ON so please select a wn. range to fit', 'danger')
                        return
                    }

                    NGauss_fit_args.index = $felixIndex
                } else {
                    NGauss_fit_args.index = []
                }

                if ($felixPeakTable.length === 0) {
                    return window.createToast('No arguments initialised yet.', 'danger')
                }

                NGauss_fit_args.fitNGauss_arguments = {}

                $felixPeakTable.forEach((f, index) => {
                    NGauss_fit_args.fitNGauss_arguments[`cen${index}`] = parseFloat(f.freq)
                    NGauss_fit_args.fitNGauss_arguments[`A${index}`] = parseFloat(f.amp)
                    NGauss_fit_args.fitNGauss_arguments[`sigma${index}`] = parseFloat(f.sig)
                })
                NGauss_fit_args = {
                    ...NGauss_fit_args,
                    location: $felixopoLocation,
                    addedFileScale,
                    addedFileCol,
                    overwrite_expfit,
                    writeFile,
                    writeFileName,
                    output_name: $felixOutputName,
                    fullfiles,
                    fitall,
                    normMethod: $normMethod,
                }

                computePy_func({
                    e,
                    pyfile: 'normline.multiGauss',
                    args: NGauss_fit_args,
                }).then((dataFromPython) => {
                    NGauss_fit_func({ dataFromPython, uniqueID })
                    if (dataFromPython[$normMethod]) {
                        console.log('Line fitted')
                        window.createToast(
                            `Line fitted with ${dataFromPython[$normMethod]['fitted_parameter'].length} gaussian function`,
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

            <button class="button is-link" on:click={() => savefile({ file: $felixPeakTable, name: savePeakfilename })}>
                Save peaks
            </button>
            <button class="button is-link" on:click={loadpeakTable}>Load peaks</button>
            <button
                class="button is-danger"
                on:click={() => {
                    $felixPlotAnnotations = []
                    $felixPeakTable = []
                    NGauss_fit_args = {}
                    relayout(currentGraph, { annotations: [] })
                    window.createToast('Cleared', 'warning')
                }}
            >
                Clear
            </button>
        </div>
    </div>
{/if}
