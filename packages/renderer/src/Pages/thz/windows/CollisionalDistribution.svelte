<script lang="ts">
    import { collisionalRateConstants } from '../stores/collisional'
    import { numberOfLevels } from '../stores/energy'
    import { collisionalTemp } from '../stores/common'
    import Textfield from '@smui/textfield'
    import SeparateWindow from '$components/SeparateWindow.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import { plot } from '../../../js/functions'
    import boltzman_distribution from '../functions/boltzman_distribution'
    import computePy_func from '$src/Pages/general/computePy'
    import WinBox from 'winbox'
    import { persistentWritable } from '$src/js/persistentStore'

    export let active: boolean = false

    const title = 'Collisional cooling'
    const plotID = 'collisionalDistributionPlot'

    let duration = 600
    const initialTemp = persistentWritable('collisionalDistribution_initialTemp', 300)
    let graphWindow: WinBox
    let windowReady = false
    let numberDensity = '2e14'
    let totalSteps = 1000
    async function computeCollisionalProcess(e?: Event) {
        try {
            const boltzman_distribution_initial_temp = boltzman_distribution($initialTemp)

            if (boltzman_distribution_initial_temp === null) return

            const { distribution: boltzmanDistribution } = boltzman_distribution_initial_temp
            const energyKeys = boltzmanDistribution.map((f) => f.label)

            const collisionalRateConstantValues: KeyStringObj = {}
            $collisionalRateConstants.forEach((f) => (collisionalRateConstantValues[f.label] = f.value))

            const boltzman_distribution_traptemp = boltzman_distribution($collisionalTemp)

            if (boltzman_distribution_traptemp === null) return

            const { distribution: boltzmanDistributionCold } = boltzman_distribution_traptemp

            const boltzmanDistributionValues: KeyStringObj<number> = {}
            boltzmanDistribution.forEach((f) => (boltzmanDistributionValues[f.label] = f.value))

            const boltzmanDistributionColdValues: KeyStringObj<number> = {}
            boltzmanDistributionCold.forEach((f) => (boltzmanDistributionColdValues[f.label] = f.value))

            const pyfile = 'ROSAA.collisionalSimulation'

            const args = {
                boltzmanDistributionValues,
                boltzmanDistributionColdValues,
                numberDensity,
                collisionalRateConstantValues,
                duration,
                energyKeys,
                numberOfLevels: $numberOfLevels,
            }

            const dataFromPython = await computePy_func({ e, pyfile, args })
            if (!dataFromPython) return

            const { data, collisionalBoltzmanPlotData, differenceFromBoltzman } = <{ [key: string]: DataFromPython }>(
                dataFromPython
            )

            plot(` Distribution: ${$collisionalTemp}K`, 'Time (s)', 'Population', data, plotID)

            plot(
                ` Distribution: ${$collisionalTemp}K`,
                'Energy Levels',
                'Population',
                collisionalBoltzmanPlotData,
                `${plotID}_collisionalBoltzman`
            )

            plot(
                `Difference: Collisional - Boltzmann`,
                'Energy Levels',
                'Difference',
                differenceFromBoltzman,
                `${plotID}_collisionalBoltzman_difference`
            )
        } catch (error) {
            window.handleError(error)
        }
    }

    $: if (windowReady) {
        setTimeout(() => graphWindow?.focus(), 100)
    }
</script>

<SeparateWindow {title} bind:active bind:windowReady bind:graphWindow maximize={false}>
    <svelte:fragment slot="header_content__slot">
        <div class="header">
            <CustomTextSwitch bind:value={$initialTemp} label="Initial temp (K)" />
            <CustomTextSwitch bind:value={$collisionalTemp} label="Coll. temp (K)" />
            <CustomTextSwitch bind:value={duration} label="duration (in ms)" />
            <Textfield bind:value={totalSteps} label="totalSteps" />
            <Textfield bind:value={numberDensity} label="Number density (cm-3)" />
            <button class="button is-link" on:click={computeCollisionalProcess}>Compute</button>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">
        <div class="graph__container">
            <div id={plotID} class="graph__div" />
            <div id="{plotID}_collisionalBoltzman" class="graph__div" />
            <div id="{plotID}_collisionalBoltzman_difference" class="graph__div" />
        </div>
    </svelte:fragment>
</SeparateWindow>

<style lang="scss">
    .header {
        display: flex;
        gap: 1em;
        align-items: center;
    }

    .graph__container {
        display: flex;
        flex-direction: column;
        row-gap: 1em;

        padding: 1em;
    }
</style>
