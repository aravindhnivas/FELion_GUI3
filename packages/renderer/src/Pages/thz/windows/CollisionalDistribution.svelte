<script lang="ts">
    import { collisionalRateConstants } from '../stores/collisional'
    import { numberOfLevels } from '../stores/energy'
    import { currentLocation, collisionalTemp, numberDensity as ND, output_dir } from '../stores/common'
    import Textfield from '@smui/textfield'
    import SeparateWindow from '$components/SeparateWindow.svelte'
    import Notify from '$components/Notify.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import { plot } from '../../../js/functions'
    import boltzman_distribution from '../functions/boltzman_distribution'
    import computePy_func from '$src/Pages/general/computePy'
    import { persistentWritable } from '$src/js/persistentStore'
    import ButtonBadge from '$src/components/ButtonBadge.svelte'

    import { save_data_to_file } from '../functions/utils'
    import WinBox from 'winbox'

    export let active: boolean = false

    const title = 'Collisional cooling'
    const plotID = 'collisionalDistributionPlot'

    let duration = 600
    const initialTemp = persistentWritable('collisionalDistribution_initialTemp', 300)
    let graphWindow: WinBox
    let windowReady = false
    let numberDensity = $ND
    let totalSteps = 1000
    let graphPlotted = false

    interface Save_plot_datas {
        [(key in 'collisional_simulation') | 'boltzman_comparision']: {
            [key: string]: {
                x: number[]
                y: number[]
            }
        }
    }
    const save_plot_datas: Save_plot_datas = {
        collisional_simulation: {},
        boltzman_comparision: {},
    }

    async function computeCollisionalProcess(e?: Event) {
        try {
            if (!numberDensity) return window.createToast('Number density is not set', 'danger')

            graphPlotted = false
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
            save_plot_datas.collisional_simulation = {}
            for (const key in data) {
                const { x, y } = data[key]
                save_plot_datas.collisional_simulation[key] = { x, y }
            }

            save_plot_datas.boltzman_comparision = {}
            const { boltzmanData, collisionalData } = collisionalBoltzmanPlotData
            save_plot_datas.boltzman_comparision.boltzmanData = {
                x: boltzmanData.x,
                y: boltzmanData.y,
                plot_kwargs: {
                    label: 'Boltzmann distribution',
                    ls: '-',
                    lw: '2',
                    color: 'black',
                },
            }
            save_plot_datas.boltzman_comparision.collisionalData = {
                x: collisionalData.x,
                y: collisionalData.y,
                plot_kwargs: {
                    label: 'Collisional stabilisation',
                    ls: 'None',
                    marker: 'o',
                    ms: '5',
                    color: 'black',
                },
            }

            plot(` Distribution: ${$collisionalTemp}K`, 'Time (s)', 'Relative population', data, plotID)

            plot(
                ` Distribution: ${$collisionalTemp}K`,
                'Energy Levels',
                'Relative population',
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
            graphPlotted = true
        } catch (error) {
            window.handleError(error)
        }
    }

    $: if (windowReady) {
        setTimeout(() => graphWindow?.focus(), 100)
    }

    $: outputFile = window.path.join($output_dir, 'collisional', `${savefile}.json`)
    let saveInfo = { msg: '', error: '' }
    const saveData = async () => {
        console.log(save_plot_datas[savefile])
        const data_to_save = JSON.stringify(save_plot_datas[savefile], null, 2)
        saveInfo = await save_data_to_file(outputFile, data_to_save)
    }

    const openFigure = (e?: Event) => {
        if (!window.fs.isFile(outputFile)) {
            window.createToast('No data to open', 'danger')
            return
        }

        const figsDir = window.path.join($output_dir, 'figs')
        window.fs.ensureDirSync(figsDir)
        const args = {
            figArgs: {
                figXlabel: $figXlabel,
                figYlabel,
                location: figsDir,
                x_type: 'string',
                y_type: 'float',
            },
            files: [outputFile],
        }

        computePy_func({ e, pyfile: 'utils.plotXY', args, general: true })
    }

    let savefile = 'collisional_simulation'
    const saveOpts = ['collisional_simulation', 'boltzman_comparision']

    const figXlabel = persistentWritable('collisionalDistribution_figXlabel', 'Time (s)')
    let figYlabel = 'Relative population'
</script>

<SeparateWindow {title} bind:active bind:windowReady bind:graphWindow maximize={false}>
    <svelte:fragment slot="header_content__slot">
        <div
            class="align no-wrap"
            on:keyup={({ code }) => {
                if (code === 'Enter') {
                    computeCollisionalProcess()
                }
            }}
        >
            <CustomTextSwitch bind:value={$initialTemp} label="Initial temp (K)" />
            <CustomTextSwitch bind:value={$collisionalTemp} label="Coll. temp (K)" />
            <CustomTextSwitch bind:value={duration} label="duration (in ms)" />
            <Textfield bind:value={totalSteps} label="totalSteps" />
            <Textfield bind:value={numberDensity} label="Number density (cm-3)" />

            <button class="button is-link" on:click={computeCollisionalProcess}>Compute</button>
        </div>

        <div class="align no-wrap">
            <CustomSelect bind:value={savefile} options={saveOpts} label="plot-type" />
            <button class="button is-link" on:click={saveData}>Save data</button>
            <Textfield bind:value={$figXlabel} label="figXlabel" />
            <Textfield bind:value={figYlabel} label="figYlabel" />

            <ButtonBadge label="Produce figure" on:click={openFigure} />
        </div>

        <Notify label={saveInfo.error || saveInfo.msg} type={saveInfo.error ? 'danger' : 'success'} />
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
    .graph__container {
        display: flex;
        flex-direction: column;
        row-gap: 1em;
        padding: 1em;
    }
</style>
