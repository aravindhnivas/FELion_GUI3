<script lang="ts">
    import { findIndex } from 'lodash-es'
    import { relayout } from 'plotly.js-basic-dist'
    import { showConfirm } from '$src/components/alert/store'
    import Layout from '$components/Layout_new.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import GetLabviewSettings from '$components/GetLabviewSettings.svelte'
    import Configs, { configs } from '$src/Pages/masspec/configs/Configs.svelte'
    import { plot } from '$src/js/functions'
    import { readMassFile } from './masspec/mass'
    import computePy_func from '$src/Pages/general/computePy'
    import ButtonBadge from '$components/ButtonBadge.svelte'

    const filetype = 'mass'
    const id = 'Masspec'

    let fileChecked: string[] = []
    let currentLocation = ''
    let currentLogScale = {}
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

        if (!window.fs.isDirectory(currentLocation)) {
            return window.createToast('Location not defined', 'danger')
        }

        if (fileChecked.length < 1) {
            return window.createToast('No files selected', 'danger')
        }
        if (filetype === 'find_peaks') {
            if (selected_file === '') return window.createToast('No files selected', 'danger')
        }

        const massfiles = window.fs.isDirectory(currentLocation)
            ? fileChecked.map((file) => window.path.resolve(currentLocation, file))
            : []
        const pyfileInfo: { [name: string]: { pyfile: string; args: Object } } = {
            mass: { pyfile: 'mass', args: { massfiles, tkplot: 'run' } },
            general: { pyfile: 'mass', args: { massfiles, tkplot: 'plot' } },
        }

        const { pyfile, args } = pyfileInfo[filetype]
        if (filetype == 'general') {
            return computePy_func({ e, pyfile, args, general: true })
        }

        if (filetype == 'mass' && massfiles) {
            const dataFromPython = await readMassFile(massfiles, `${activePlotID}-${btnID}`)
            if (dataFromPython === null) return
            console.log({ dataFromPython })
            const logScale = currentLogScale[activeTabID]
            plot('Mass spectrum', 'Mass [u]', 'Counts', dataFromPython, activePlotID, logScale, true)
            // graphPlotted = true
            return
        }
    }

    const linearlogCheck = () => {
        const logScale = currentLogScale[activeTabID]
        const layout: Partial<Plotly.Layout> = {
            yaxis: { title: 'Counts', type: logScale ? 'log' : undefined },
        }
        const plotHTML = document.getElementById(activePlotID)
        if (plotHTML?.data) relayout(activePlotID, layout)
    }

    let fullfileslist: string[] = []

    const plotID = 'mplot'
    let btnID = 'masspec-plot-btn'

    let display = window.db.get('active_tab') === id ? 'block' : 'none'

    let activeTabID = ''
    $: activePlotID = `${plotID}-${activeTabID}`

    let attributes = []
    $: currentActiveInd_Attributes = findIndex(attributes, (o) => o.id === activeTabID)
    $: if (activePlotID && attributes.length > 0) {
        ;({ fileChecked, currentLocation, fullfileslist } = attributes[currentActiveInd_Attributes])
    }
    // $: console.warn(currentLogScale)
</script>

<Layout
    bind:attributes
    {display}
    {filetype}
    {id}
    on:activeTabChange={({ detail: { id } }) => {
        activeTabID = id
        currentLogScale[activeTabID] ??= true
        // console.warn('mass activeTabChange', id)
    }}
>
    <svelte:fragment slot="buttonContainer" let:id>
        <div class="align " style="align-items: center;">
            <button class="button is-link" id={`${plotID}-${id}-${btnID}`} on:click={(e) => plotData({ e: e })}>
                Masspec Plot</button
            >
            <GetLabviewSettings {currentLocation} {fullfileslist} {fileChecked} />
            <ButtonBadge on:click={(e) => plotData({ e, filetype: 'general' })} label="Open in Matplotlib" />
            {#if currentLogScale[activeTabID] !== undefined}
                <CustomSwitch
                    style="margin: 0 1em;"
                    on:change={linearlogCheck}
                    bind:selected={currentLogScale[activeTabID]}
                    label="Log"
                />
            {/if}
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer" let:id>
        <div id={`${plotID}-${id}`} class="graph__div" />
    </svelte:fragment>

    <svelte:fragment slot="config">
        <div class="align">
            <Configs />
        </div>
    </svelte:fragment>
</Layout>
