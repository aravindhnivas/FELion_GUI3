<script lang="ts">
    // import { findIndex } from 'lodash-es'
    import { relayout } from 'plotly.js-basic-dist'
    import { showConfirm } from '$src/components/alert/store'
    import Layout from '$components/Layout.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import GetLabviewSettings from '$components/GetLabviewSettings.svelte'
    import Configs, { configs } from '$src/Pages/masspec/configs/Configs.svelte'
    import { plot } from '$src/js/functions'
    import { readMassFile } from './masspec/mass'
    import computePy_func from '$src/Pages/general/computePy'
    import ButtonBadge from '$components/ButtonBadge.svelte'

    // const filetype = 'mass'
    // const id = 'Masspec'

    export let id = 'Masspec'
    export let display = 'grid'
    export let saveLocationToDB = true

    const filetype = 'mass'
    const uniqueID = `${id}-${window.getID()}`

    setContext('uniqueID', uniqueID)
    setContext('saveLocationToDB', saveLocationToDB)

    let fileChecked: string[] = []
    let currentLocation = ''

    const plotID = `${uniqueID}-mplot`
    const btnID = `${uniqueID}-masspec-plot-btn`

    $: massfiles = window.fs.isDirectory(currentLocation)
        ? fileChecked.map((file) => window.path.resolve(currentLocation, file))
        : []
    $: if (massfiles.length > 0) {
        plotData()
    }

    let selected_file = ''

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
                    if (response?.toLowerCase() === 'cancel') {
                        fileChecked = []
                        // fileChecked = fullfileslist.slice(0, $configs['max_files_to_plot'].value)
                        // console.log(fullfileslist)
                        return
                    }
                    plotData({
                        e,
                        filetype,
                        overwride_file_limit_warning: true,
                    })
                },
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

        // const massfiles = window.fs.isDirectory(currentLocation)
        //     ? fileChecked.map((file) => window.path.resolve(currentLocation, file))
        //     : []
        const pyfileInfo: { [name: string]: { pyfile: string; args: Object } } = {
            mass: { pyfile: 'mass', args: { massfiles, tkplot: 'run' } },
            general: { pyfile: 'mass', args: { massfiles, tkplot: 'plot' } },
        }

        const { pyfile, args } = pyfileInfo[filetype]
        if (filetype == 'general') {
            return computePy_func({ e, pyfile, args, general: true })
        }

        if (filetype == 'mass' && massfiles) {
            const dataFromPython = await readMassFile(massfiles, btnID)
            if (dataFromPython === null) return
            console.log({ dataFromPython })
            plot('Mass spectrum', 'Mass [u]', 'Counts', dataFromPython, plotID, logScale, true)
            // graphPlotted = true
            return
        }
    }

    const linearlogCheck = () => {
        const layout: Partial<Plotly.Layout> = {
            yaxis: { title: 'Counts', type: logScale ? 'log' : undefined },
        }
        const plotHTML = document.getElementById(plotID)
        if (plotHTML?.data) relayout(plotID, layout)
    }

    let fullfileslist: string[] = []
    let logScale = true
</script>

<Layout {display} {filetype} {id} bind:currentLocation bind:fileChecked bind:fullfileslist>
    <svelte:fragment slot="buttonContainer">
        <div class="align " style="align-items: center;">
            <button class="button is-link" id={btnID} on:click={(e) => plotData({ e: e })}> Masspec Plot</button>
            <GetLabviewSettings {currentLocation} {fullfileslist} {fileChecked} />
            <ButtonBadge on:click={(e) => plotData({ e, filetype: 'general' })} label="Open in Matplotlib" />
            <!-- {#if currentLogScale[activeTabID] !== undefined} -->
            <CustomSwitch style="margin: 0 1em;" on:change={linearlogCheck} bind:selected={logScale} label="Log" />
            <!-- {/if} -->
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer">
        <div id={plotID} class="graph__div" />
    </svelte:fragment>

    <svelte:fragment slot="config">
        <div class="align">
            <Configs />
        </div>
    </svelte:fragment>
</Layout>
