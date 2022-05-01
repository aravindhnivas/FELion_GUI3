<script>
    import Layout from '$components/Layout.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import CustomIconSwitch from '$components/CustomIconSwitch.svelte'
    import GetLabviewSettings from '$components/GetLabviewSettings.svelte'
    import { relayout } from 'plotly.js/dist/plotly-basic'
    import { plot, plotlyEventsInfo } from '$src/js/functions'
    import { readMassFile } from './masspec/mass'
    import computePy_func from '$src/Pages/general/computePy'
    import { onDestroy } from 'svelte'

    /////////////////////////////////////////////////////////////////////////

    // Initialisation
    const filetype = 'mass'
    const id = 'Masspec'
    let fileChecked = []
    let currentLocation = ''
    $: massfiles = fs.existsSync(currentLocation)
        ? fileChecked.map((file) => pathResolve(currentLocation, file))
        : []
    $: if (massfiles.length > 0) plotData()

    let openShell = false
    let graphPlotted = false
    // let toggleRow1 = true
    let logScale = true
    let selected_file = ''

    // let peak_width = 2
    // let peak_height = 40
    // let peak_prominance = 3
    let keepAnnotaions = true

    async function plotData({ e = null, filetype = 'mass' } = {}) {
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
            return computePy_func({ e, pyfile, args, general: true, openShell })
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
    let display = db.get('active_tab') === id ? 'block' : 'none'
</script>

<Layout
    {filetype}
    {display}
    bind:fullfileslist
    {id}
    bind:currentLocation
    bind:fileChecked
    {graphPlotted}
>
    <svelte:fragment slot="buttonContainer">
        <div class="align " style="align-items: center;">
            <button class="button is-link" on:click={(e) => plotData({ e: e })}>
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

            <CustomIconSwitch
                style="padding:0;"
                bind:toggler={openShell}
                icons={['settings_ethernet', 'code']}
            />
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
</Layout>
