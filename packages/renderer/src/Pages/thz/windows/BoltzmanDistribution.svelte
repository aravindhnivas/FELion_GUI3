<script>
    import SeparateWindow from '$components/SeparateWindow.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import { plot } from '../../../js/functions'
    import boltzman_distribution from '../functions/boltzman_distribution'
    import { sumBy } from 'lodash-es'

    export let active
    export let trapTemp
    export let energyLevels

    export let zeemanSplit
    export let energyUnit
    export let electronSpin

    const title = 'Boltzman Distribution'
    const plotID = 'boltzmanDistributionPlot'
    let graphWindow = null,
        windowReady = false

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
            const data = {
                x: energyLevel,
                y: populations,
                mode: 'lines+markers',
                showlegend: true,
                name: `Temp: ${trapTemp}K, Z: ${partitionValue}, Total: ${totalSum}`,
            }
            const dataToPlot = { data }
            plot(
                `${title}: ${trapTemp}K`,
                'Energy Levels',
                'Population',
                dataToPlot,
                plotID
            )
            console.log('Plotted')
        }
    }
    $: if (windowReady) {
        setTimeout(() => graphWindow.focus(), 100)
    }
    $: if (windowReady && trapTemp > 0) {
        plotGraph()
    }
</script>

<SeparateWindow
    {title}
    bind:active
    bind:windowReady
    bind:graphWindow
    maximize={false}
>
    <svelte:fragment slot="header_content__slot">
        <div class="align">
            <CustomTextSwitch bind:value={trapTemp} label="Temperature (K)" />
            <button class="button is-link" on:click={plotGraph}>Compute</button>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">
        <div id={plotID} class="graph__div" />
    </svelte:fragment>
</SeparateWindow>
