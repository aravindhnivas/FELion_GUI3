<script>
    import { relayout, addTraces, deleteTraces } from 'plotly.js-basic-dist'
    import { plot, plotlyEventsInfo } from '$src/js/functions'
    import computePy_func from '$src/Pages/general/computePy'
    import Layout from '$components/Layout.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import STable from '$components/STable.svelte'
    import THzFitParamsTable from './thz/components/THzFitParamsTable.svelte'
    import Matplotlib from './thz/Matplotlib.svelte'
    import { onDestroy } from 'svelte'

    import Textfield from '@smui/textfield'

    // const filetype = 'thz'
    // const id = 'THz'

    export let id = 'THz'
    export let display = 'grid'
    export let saveLocationToDB = true

    const filetype = 'thz'
    const uniqueID = `${id}-${window.getID()}`

    setContext('uniqueID', uniqueID)
    setContext('saveLocationToDB', saveLocationToDB)

    let fileChecked = []
    let currentLocation = ''
    $: thzfiles = fileChecked.map((file) => window.path.resolve(currentLocation, file))

    let binSize = 10
    let binData = true
    let showall = false
    let saveInMHz = false
    let showRawData = false
    let graphPlotted = false

    let fittedParamsTable = []
    const rowKeys = ['filename', 'freq', 'amp', 'sigma', 'gamma', 'fwhm']
    const headKeys = ['Filename', 'freq (MHz)', 'amp', 'sigma', 'gamma', 'FWHM']
    let rawDataProcessed = { data: null }
    let dataProcessed = {}
    let numOfFittedLines = 0

    async function plotData({ e = null, filetype = 'thz', tkplot = false, justPlot = false, general = {} } = {}) {
        if (fileChecked.length === 0 && filetype === 'thz') {
            return window.createToast('No files selected', 'danger')
        }
        const thz_args = {
            thzfiles,
            binData,
            tkplot,
            binSize,
            justPlot,
            saveInMHz,
            paramsTable,
            fitfile,
            fitMethod,
            varyAll,
            plotIndex,
            avgfilename,
        }
        const pyfileInfo = {
            general,
            thz: { pyfile: 'THz.thz_scan', args: thz_args },
        }
        const { pyfile, args } = pyfileInfo[filetype]
        if (tkplot) {
            filetype = 'general'
        }

        if (filetype == 'general') {
            return computePy_func({ e, pyfile, args, general: true })
        }
        if (!justPlot && paramsTable.length < 1) return window.createToast('No initial guesses were given', 'danger')
        const dataFromPython = await computePy_func({ e, pyfile, args })
        if (!dataFromPython) return

        const fitPlot = !justPlot

        if (filetype == 'thz') {
            if (fitPlot) {
                const { averaged, individual } = dataFromPython['thz']
                const fitDataProcessed = { ...individual, ...averaged }
                addTraces(`${uniqueID}-thzPlot`, fitDataProcessed[fitfile + '_fit'])
                numOfFittedLines++
                const receivedPramsTable = dataFromPython?.fittedParamsTable || []
                fittedParamsTable = [...fittedParamsTable, ...receivedPramsTable].map((row) => ({
                    ...row,
                    id: window.getID(),
                }))
            } else {
                const { averaged, individual } = dataFromPython['thz']
                dataProcessed = { ...individual, ...averaged }
                rawDataProcessed.data = dataFromPython['resOnOff_Counts']
                numOfFittedLines = 0
            }
            graphPlotted = true
        }
    }

    let openTable = false
    let paramsTable = []

    let fitfile = 'averaged'
    let fitMethod = 'lorentz'
    const graphIDs = [`${uniqueID}-thzPlot`, `${uniqueID}-resOnOffPlot`]

    onDestroy(() => {
        graphIDs.forEach((graphID) => {
            if ($plotlyEventsInfo[graphID]) {
                $plotlyEventsInfo[graphID].eventCreated = false
                $plotlyEventsInfo[graphID].annotations = []
            }
        })
    })

    let varyAll = true
    const [title, xlabel, ylabel] = ['THz Scan: Depletion (%)', 'Frequency (GHz)', 'Depletion (%)']

    $: if (showall && dataProcessed) {
        plot(title, xlabel, ylabel, dataProcessed, `${uniqueID}-thzPlot`, null, true)
        if (!plotlySelectCreated) {
            makePlotlySelect()
        }
    } else if (plotfile && dataProcessed?.[plotfile] && graphPlotted) {
        const dataToPlot = { data: dataProcessed[plotfile] }
        plot(title, xlabel, ylabel, dataToPlot, `${uniqueID}-thzPlot`, null, true)
        if (!plotlySelectCreated) {
            makePlotlySelect()
        }
    }

    $: if (showall && rawDataProcessed?.data) {
        plot('THz Scan', 'Frequency (GHz)', 'Counts', rawDataProcessed.data, `${uniqueID}-resOnOffPlot`)
    } else if (plotfile !== 'averaged' && rawDataProcessed?.data) {
        const dataToPlot = {}
        dataToPlot[`${plotfile}_On`] = rawDataProcessed.data[`${plotfile}_On`]
        dataToPlot[`${plotfile}_Off`] = rawDataProcessed.data[`${plotfile}_Off`]
        plot('THz Scan', 'Frequency (GHz)', 'Counts', dataToPlot, `${uniqueID}-resOnOffPlot`)
    }

    let plotfile = 'averaged'
    let avgfilename = 'averaged'
    let plotIndex = []
    let plotlySelectCreated = false

    const makePlotlySelect = () => {
        const graphDIV = document.getElementById(`${uniqueID}-thzPlot`)
        graphDIV.on('plotly_selected', (data) => {
            try {
                if (!data) return
                console.log(data)

                const { range } = data
                plotIndex = range.x
                console.log(range, plotIndex)
            } catch (error) {
                window.handleError(error)
            }
        })
        console.log('plotlySelectCreated', plotlySelectCreated)
        plotlySelectCreated = true
    }

    // let display = window.db.get('active_tab') === id ? 'block' : 'none'

    let toggle_options = false
    let fit_options_div = false
    let open_matplotlib = false

    const matplotlib_plot = async (event) => {
        const { e, args } = event.detail

        if (args.thzfiles.length === 0) {
            return window.createToast('No files selected', 'danger')
        }
        return computePy_func({ e, pyfile: 'THz.thz_matplotlib', args, general: true })
    }
</script>

<THzFitParamsTable bind:active={openTable} bind:paramsTable bind:varyAll {currentLocation} {fitMethod} />

<Matplotlib bind:active={open_matplotlib} {currentLocation} on:submit={matplotlib_plot} />

<Layout {filetype} {graphPlotted} {id} {display} bind:currentLocation bind:fileChecked>
    <svelte:fragment slot="buttonContainer">
        <div class="align v-center">
            <button
                class="button is-link"
                on:click={(e) => {
                    plotData({ e: e, justPlot: true })
                }}
            >
                Plot
            </button>
            <CustomCheckbox bind:value={binData} label="Bin" />
            <CustomTextSwitch bind:value={binSize} label="binSize (kHz)" step="0.1" />
            <button class="button is-link" on:click={() => (fit_options_div = !fit_options_div)}>Fit options</button>
            <button class="button is-link" on:click={() => (toggle_options = !toggle_options)}>More options</button>
        </div>

        <div class="align" style="justify-content: flex-end;" class:hide={!fit_options_div}>
            <i role="presentation" class="material-symbols-outlined" on:click={() => (openTable = true)}>settings</i>
            <CustomSelect bind:value={fitfile} label="fitfile" options={[...fileChecked, 'averaged']} />
            <CustomSelect bind:value={fitMethod} label="fit method" options={['gaussian', 'lorentz', 'voigt']} />
            <button
                class="button is-link"
                on:click={(e) => {
                    plotData({ e: e })
                }}>Fit</button
            >
        </div>

        <div class="align" class:hide={!toggle_options}>
            <CustomSelect bind:value={plotfile} label="plotfile" options={[...fileChecked, 'averaged']} />
            <Textfield bind:value={avgfilename} label="saveAs (binned)" />
            <CustomCheckbox bind:value={saveInMHz} label="saveInMHz" />
            <CustomCheckbox bind:value={showRawData} label="showRawData" />
            <CustomCheckbox bind:value={showall} label="show all" />
            <button class="button is-link" on:click={(e) => (open_matplotlib = true)}>Open in Matplotlib</button>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer">
        <div id="{uniqueID}-resOnOffPlot" class="graph__div" class:hide={!showRawData} />
        <div id="{uniqueID}-thzPlot" class="graph__div" />
    </svelte:fragment>

    <svelte:fragment slot="plotContainer_functions">
        <div class="align">
            <button
                class="button is-warning"
                on:click={() => {
                    try {
                        if (numOfFittedLines > 0) {
                            deleteTraces(`${uniqueID}-thzPlot`, -1)
                            numOfFittedLines--
                        }
                    } catch (error) {
                        window.handleError(error)
                    }
                }}
            >
                Clear last fit
            </button>
            <button
                class="button is-warning"
                on:click={() => {
                    $plotlyEventsInfo[`${uniqueID}-thzPlot`].annotations = []
                    relayout(`${uniqueID}-thzPlot`, { annotations: [] })
                }}
            >
                Clear Annotations
            </button>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer_reports">
        <STable
            {rowKeys}
            {headKeys}
            bind:rows={fittedParamsTable}
            closeableRows={true}
            sortable={true}
            configDir={window.path.join(currentLocation, 'EXPORT')}
            options_filter={'.thz.table.json'}
        />
    </svelte:fragment>
</Layout>
