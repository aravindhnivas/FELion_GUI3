<script>
    import { showConfirm } from '$src/components/alert/store'
    import Layout from '$components/Layout.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import GetLabviewSettings from '$components/GetLabviewSettings.svelte'
    import Configs, { configs } from '$src/Pages/masspec/configs/Configs.svelte'
    import { relayout } from 'plotly.js/dist/plotly-basic'
    import { plot, plotlyEventsInfo } from '$src/js/functions'
    import { readMassFile } from './masspec/mass'
    import computePy_func from '$src/Pages/general/computePy'
    import { onDestroy } from 'svelte'
    /////////////////////////////////////////////////////////////////////////

    const filetype = 'mass'
    const id = 'Masspec'

    let fileChecked = []
    let currentLocation = ''

    $: massfiles = fs.existsSync(currentLocation)
        ? fileChecked.map((file) => pathResolve(currentLocation, file))
        : []
    $: if (massfiles.length > 0) plotData()
    // $: console.log($configs.max_files_to_plot.value)

    let graphPlotted = false
    let logScale = true
    let selected_file = ''
    let keepAnnotaions = true

    async function plotData({
        e = null,
        filetype = 'mass',
        overwride_file_limit_warning = false,
    } = {}) {
        if (
            !overwride_file_limit_warning &&
            fileChecked.length > $configs['max_files_to_plot'].value
        ) {
            showConfirm.push({
                title:
                    'Too many files: allowed is' +
                    $configs['max_files_to_plot'].value,
                content:
                    'Do you want to plot ' + fileChecked.length + ' files?',
                callback: (response) => {
                    if (!response) return console.warn('response: ', response)
                    console.log(response)
                    if (response?.toLowerCase() === 'cancel') return
                    plotData({
                        e,
                        filetype,
                        overwride_file_limit_warning: true,
                    })
                },
            })
            return
        }

        if (!fs.existsSync(currentLocation)) {
            return window.createToast('Location not defined', 'danger')
        }

        if (fileChecked.length < 1) {
            return window.createToast('No files selected', 'danger')
        }
        if (filetype === 'find_peaks') {
            if (selected_file === '')
                return window.createToast('No files selected', 'danger')
        }

        const pyfileInfo = {
            mass: { pyfile: 'mass', args: { massfiles, tkplot: 'run' } },
            general: { pyfile: 'mass', args: { massfiles, tkplot: 'plot' } },
        }

        const { pyfile, args } = pyfileInfo[filetype]

        if (filetype == 'general') {
            return computePy_func({ e, pyfile, args, general: true })
        }

        if (filetype == 'mass' && massfiles) {
            const [dataFromPython] = await readMassFile(massfiles)

            if (!dataFromPython) return
            if (!keepAnnotaions) {
                $plotlyEventsInfo['mplot'].annotations = []
            }

            plot(
                'Mass spectrum',
                'Mass [u]',
                'Counts',
                dataFromPython,
                'mplot',
                logScale ? 'log' : 'linear',
                true
            )
            if (keepAnnotaions) {
                relayout('mplot', {
                    annotations: $plotlyEventsInfo['mplot'].annotations,
                })
            }

            graphPlotted = true
            return
        }
    }

    const linearlogCheck = () => {
        const layout = {
            yaxis: { title: 'Counts', type: logScale ? 'log' : null },
        }
        if (graphPlotted) relayout('mplot', layout)
    }

    let fullfileslist = []

    onDestroy(() => {
        if ($plotlyEventsInfo.mplot) {
            $plotlyEventsInfo.mplot.eventCreated = false
            $plotlyEventsInfo.mplot.annotations = []
        }
    })
    let display = window.db.get('active_tab') === id ? 'block' : 'none'
</script>

<Layout
    {filetype}
    {display}
    bind:fullfileslist
    {id}
    bind:currentLocation
    {graphPlotted}
    bind:fileChecked
>
    <svelte:fragment slot="buttonContainer">
        <div class="align " style="align-items: center;">
            <button
                class="button is-link"
                id="masspec-plot-btn"
                on:click={(e) => plotData({ e: e })}
            >
                Masspec Plot</button
            >

            <GetLabviewSettings
                {currentLocation}
                {fullfileslist}
                {fileChecked}
            />
            <button
                class="button is-link"
                on:click={(e) => plotData({ e: e, filetype: 'general' })}
            >
                Open in Matplotlib</button
            >

            <CustomSwitch
                style="margin: 0 1em;"
                on:SMUISwitch:change={linearlogCheck}
                bind:selected={logScale}
                label="Log"
            />
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer"
        ><div id="mplot" class="graph__div" /></svelte:fragment
    >

    <svelte:fragment slot="plotContainer_functions">
        <div class="align" style="justify-content: flex-end;">
            <CustomSwitch
                style="margin: 0 1em;"
                bind:selected={keepAnnotaions}
                label="Keep Annotaions"
            />
            <button
                class="button is-danger"
                on:click={() => {
                    $plotlyEventsInfo['mplot'].annotations = []
                    relayout('mplot', { annotations: [] })
                }}>Clear</button
            >
        </div>
    </svelte:fragment>

    <svelte:fragment slot="config">
        <div class="align">
            <Configs />
        </div>
    </svelte:fragment>
</Layout>
