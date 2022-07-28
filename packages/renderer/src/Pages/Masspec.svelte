<script lang="ts">
    import { showConfirm } from '$src/components/alert/store'
    import Layout from '$components/Layout.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import GetLabviewSettings from '$components/GetLabviewSettings.svelte'
    import Configs, { configs } from '$src/Pages/masspec/configs/Configs.svelte'
    import { relayout } from 'plotly.js/dist/plotly-basic'
    import { plot, plotlyEventsInfo } from '$src/js/functions'
    import { readMassFile, MassData } from './masspec/mass'
    import computePy_func from '$src/Pages/general/computePy'
    import { onDestroy } from 'svelte'
    import ButtonBadge from '$components/ButtonBadge.svelte'

    const filetype = 'mass'
    const id = 'Masspec'

    let fileChecked: string[] = []
    let currentLocation = ''

    $: massfiles = window.fs.isDirectory(currentLocation)
        ? fileChecked.map((file) => window.path.resolve(currentLocation, file))
        : []
    $: if (massfiles.length > 0) plotData()

    let graphPlotted = false
    let logScale = true
    let selected_file = ''
    let keepAnnotaions = true

    async function plotData({
        e = undefined,
        filetype = 'mass',
        overwride_file_limit_warning = false,
    }: {
        e?: ButtonClickEvent
        filetype?: 'mass' | 'general' | 'find_peaks'
        overwride_file_limit_warning?: boolean
    } = {}) {
        if (!overwride_file_limit_warning && fileChecked.length > $configs['max_files_to_plot'].value) {
            showConfirm.push({
                title: 'Too many files: safe limit is' + $configs['max_files_to_plot'].value,
                content: 'Do you want to plot ' + fileChecked.length + ' files?',
                callback: (response: string) => {
                    if (!response) return console.warn('response: ', response)
                    console.log(response)
                    if (response?.toLowerCase() === 'cancel') return
                    plotData({
                        e,
                        filetype,
                        overwride_file_limit_warning: true,
                    })
                },
                open: false,
            })
            return
        }

        if (!window.fs.isDirectory(currentLocation)) {
            return window.createToast('Location not defined', 'danger')
        }

        if (fileChecked.length < 1) {
            return window.createToast('No files selected', 'danger')
        }
        if (filetype === 'find_peaks') {
            if (selected_file === '') return window.createToast('No files selected', 'danger')
        }

        const pyfileInfo: { [name: string]: { pyfile: string; args: Object } } = {
            mass: { pyfile: 'mass', args: { massfiles, tkplot: 'run' } },
            general: { pyfile: 'mass', args: { massfiles, tkplot: 'plot' } },
        }

        const { pyfile, args } = pyfileInfo[filetype]
        if (filetype == 'general') {
            return computePy_func({ e, pyfile, args, general: true })
        }

        if (filetype == 'mass' && massfiles) {
            const computedData = await readMassFile(massfiles)
            if (computedData === undefined) return window.createToast('No data computed', 'danger')

            console.log({ computedData })
            const [dataFromPython, error] = computedData as [MassData | null, Error | string]
            if (error instanceof Error || (error as string)) return window.handleError(error)
            if (dataFromPython === null) return window.createToast('No data found', 'danger')

            if (!keepAnnotaions) {
                $plotlyEventsInfo['mplot'].annotations = []
            }
            console.log({ dataFromPython })
            plot('Mass spectrum', 'Mass [u]', 'Counts', dataFromPython, 'mplot', logScale, true)
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

    let fullfileslist: string[] = []

    onDestroy(() => {
        if ($plotlyEventsInfo.mplot) {
            $plotlyEventsInfo.mplot.eventCreated = false
            $plotlyEventsInfo.mplot.annotations = []
        }
    })
    let display = window.db.get('active_tab') === id ? 'block' : 'none'
</script>

<Layout {filetype} {display} bind:fullfileslist {id} bind:currentLocation {graphPlotted} bind:fileChecked>
    <svelte:fragment slot="buttonContainer">
        <div class="align " style="align-items: center;">
            <button class="button is-link" id="masspec-plot-btn" on:click={(e) => plotData({ e: e })}>
                Masspec Plot</button
            >
            <GetLabviewSettings {currentLocation} {fullfileslist} {fileChecked} />
            <ButtonBadge on:click={(e) => plotData({ e, filetype: 'general' })} label="Open in Matplotlib" />
            <CustomSwitch style="margin: 0 1em;" on:change={linearlogCheck} bind:selected={logScale} label="Log" />
        </div>
    </svelte:fragment>
    <svelte:fragment slot="plotContainer">
        <div id="mplot" class="graph__div" />
        <!-- <DygraphComponent id="dygraph-mplot" /> -->
    </svelte:fragment>

    <svelte:fragment slot="plotContainer_functions">
        <div class="align" style="justify-content: flex-end;">
            <CustomSwitch style="margin: 0 1em;" bind:selected={keepAnnotaions} label="Keep Annotaions" />
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
