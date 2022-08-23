<script lang="ts">
    import { trapTemp, currentLocation, output_dir } from '../stores/common'
    import SeparateWindow from '$components/SeparateWindow.svelte'
    import Notify from '$components/Notify.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import { plot } from '../../../js/functions'
    import boltzman_distribution from '../functions/boltzman_distribution'
    import { sumBy } from 'lodash-es'
    import computePy_func from '$src/Pages/general/computePy'
    import ButtonBadge from '$src/components/ButtonBadge.svelte'
    import WinBox from 'winbox'
    import { save_data_to_file } from '../functions/utils'

    export let active = false
    export let graphWindow: WinBox | null = null

    const title = 'Boltzman Distribution'
    const plotID = 'boltzmanDistributionPlot'

    let windowReady = false

    let plotData: (string[] | number[])[] = [[], []]

    function plotGraph() {
        const computedData = boltzman_distribution($trapTemp)
        if (computedData === null) return

        const { distribution, partitionValue } = computedData
        console.log('Computing', distribution)

        const totalSum = sumBy(distribution, (e) => e.value)
        const energyLevel = distribution.map((e) => e.label)
        const populations = distribution.map((e) => e.value)
        plotData = [energyLevel, populations]

        const data: PlotData = {
            x: energyLevel,
            y: populations,
            mode: 'lines+markers',
            showlegend: true,
            name: `Temp: ${$trapTemp}K, Z: ${partitionValue.toFixed(2)}, Total: ${totalSum.toFixed(2)}`,
        }
        const dataToPlot = { data }
        plot(`${title}: ${$trapTemp}K`, 'Energy Levels', 'Population', dataToPlot, plotID)
        console.log('Plotted')
    }

    $: if (windowReady) {
        setTimeout(() => graphWindow?.focus(), 100)
    }

    $: if (windowReady && $trapTemp > 0) {
        plotGraph()
    }

    let saveInfo = { msg: '', error: '' }
    $: outputFile = window.path.join($output_dir, `boltzman/boltzman_distribution${$trapTemp}K.dat`)

    const saveData = async () => {
        const length = plotData[0].length
        let writeContent = '# Energy Levels\t Population \n'
        for (let i = 0; i < length; i++) {
            writeContent += `${plotData[0][i]}\t${plotData[1][i]}\n`
        }
        saveInfo = await save_data_to_file(outputFile, writeContent)
    }

    const openFigure = (e?: Event) => {
        if (!window.fs.isFile(outputFile)) {
            window.createToast('No data to open', 'danger')
            return
        }

        const figsDir = window.path.join($currentLocation, '../output/figs')
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
            <CustomTextSwitch bind:value={$trapTemp} label="Temperature (K)" />
            <button class="button is-link" on:click={plotGraph}>Compute</button>
            <button class="button is-link" on:click={saveData}>Save data</button>
            <ButtonBadge label="Produce figure" on:click={openFigure} />
        </div>

        <Notify label={saveInfo.error || saveInfo.msg} type={saveInfo.error ? 'danger' : 'success'} />
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">
        <div id={plotID} class="graph__div" />
    </svelte:fragment>
</SeparateWindow>
