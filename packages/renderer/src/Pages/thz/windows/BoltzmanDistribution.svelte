<script lang="ts">
    import SeparateWindow from '$components/SeparateWindow.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import { plot } from '../../../js/functions'
    import boltzman_distribution from '../functions/boltzman_distribution'
    import { sumBy } from 'lodash-es'
    import computePy_func from '$src/Pages/general/computePy'
    import ButtonBadge from '$src/components/ButtonBadge.svelte'
    import WinBox from 'winbox'

    export let active = false
    export let trapTemp: string | number
    export let energyLevels: ValueLabel<number>[] = []
    export let zeemanSplit: boolean
    export let energyUnit: 'cm-1' | 'MHz'
    export let electronSpin: boolean
    export let graphWindow: WinBox | null = null
    export let currentLocation: string = ''

    const title = 'Boltzman Distribution'
    const plotID = 'boltzmanDistributionPlot'

    let windowReady = false

    let plotData = [[], []]

    function plotGraph() {
        const { distribution, partitionValue } = boltzman_distribution({
            energyLevels,
            trapTemp,
            electronSpin,
            zeemanSplit,
            energyUnit,
        })
        // console.log()
        console.log('Computing', distribution)
        if (distribution) {
            const totalSum = sumBy(distribution, (e) => e.value).toFixed(2)
            const energyLevel = distribution.map((e) => e.label)
            const populations = distribution.map((e) => e.value)
            plotData = [energyLevel, populations]
            const data = {
                x: energyLevel,
                y: populations,
                mode: 'lines+markers',
                showlegend: true,
                name: `Temp: ${trapTemp}K, Z: ${partitionValue}, Total: ${totalSum}`,
            }
            const dataToPlot = { data }
            plot(`${title}: ${trapTemp}K`, 'Energy Levels', 'Population', dataToPlot, plotID)
            console.log('Plotted')
        }
    }

    $: if (windowReady) {
        setTimeout(() => graphWindow?.focus(), 100)
    }
    $: if (windowReady && trapTemp > 0) {
        plotGraph()
    }

    const saveInfo = { msg: '', error: '' }
    $: outputFile = window.path.join(currentLocation, '../output/datas', `boltzman_distribution${trapTemp}K.dat`)

    const saveData = async () => {
        console.log({ currentLocation, plotData })
        window.fs.ensureDirSync(window.path.dirname(outputFile))

        const length = plotData[0].length

        let writeContent = '# Energy Levels\t Population \n'
        for (let i = 0; i < length; i++) {
            writeContent += `${plotData[0][i]}\t${plotData[1][i]}\n`
        }

        const output = await window.fs.writeFile(outputFile, writeContent)

        if (window.fs.isError(output)) {
            saveInfo.error = output
            return window.handleError(output)
        }
        saveInfo.msg = `Saved to ${outputFile}`
        window.createToast(`Data saved`)
    }

    const openFigure = (e) => {
        if (!window.fs.isFile(outputFile)) {
            window.createToast('No data to open', 'danger')
            return
        }

        const figsDir = window.path.join(currentLocation, '../output/figs')
        window.fs.ensureDirSync(figsDir)

        const args = {
            figArgs: {
                figXlabel: 'J',
                figYlabel: 'Population ratio',
                location: figsDir,
                x_type: 'string',
                y_type: 'float',
            },
            files: [outputFile],
        }
        computePy_func({ e, pyfile: 'utils.plotXY', args, general: true })
    }
</script>

<SeparateWindow {title} bind:active bind:windowReady bind:graphWindow maximize={false}>
    <svelte:fragment slot="header_content__slot">
        <div class="align">
            <CustomTextSwitch bind:value={trapTemp} label="Temperature (K)" />
            <button class="button is-link" on:click={plotGraph}>Compute</button>
            <button class="button is-link" on:click={saveData}>Save data</button>
            <ButtonBadge label="Produce figure" on:click={openFigure} />
        </div>

        {#if saveInfo.error || saveInfo.msg}
            <div class="block mt-5">
                <span class="notification  is-success" class:is-danger={saveInfo.error}>
                    {saveInfo.error || saveInfo.msg}
                    <button
                        class="delete is-danger"
                        on:click={() => {
                            saveInfo.error = ''
                            saveInfo.msg = ''
                        }}
                    />
                </span>
            </div>
        {/if}
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">
        <div id={plotID} class="graph__div" />
    </svelte:fragment>
</SeparateWindow>
