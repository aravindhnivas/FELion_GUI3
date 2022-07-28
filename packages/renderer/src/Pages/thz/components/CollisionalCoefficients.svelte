<script lang="ts">
    import Textfield from '@smui/textfield'
    import { find, cloneDeep } from 'lodash-es'
    import { onMount } from 'svelte'
    import balance_distribution from '../functions/balance_distribution'
    import CollisionalDistribution from '../windows/CollisionalDistribution.svelte'
    import CollisionalRateConstantPlot from '../windows/CollisionalRateConstantPlot.svelte'
    import { browse } from '$components/Layout.svelte'

    export let energyUnit: string
    export let zeemanSplit: boolean
    export let energyLevels: ValueLabel[]

    export let electronSpin: boolean
    export let numberOfLevels: number
    export let numberDensity = '4e14'
    export let collisionalRates: ValueLabel[] = []
    export let collisionalTemp: number | null = null
    export let collisionalFilename = ''
    export let collisionalCoefficient: ValueLabel[] = []
    export let collisionalCoefficient_balance: ValueLabel[] = []

    let collisionalWindow = false
    $: collisionalRateConstants = [...collisionalCoefficient, ...collisionalCoefficient_balance]
    $: collisionalArgs = {
        energyUnit,
        zeemanSplit,
        energyLevels,
        electronSpin,
        numberOfLevels,
        collisionalTemp,
        collisionalRateConstants,
    }

    const compteCollisionalBalanceConstants = () => {
        const balanceArgs = {
            energyLevels,
            collisionalTemp,
            electronSpin,
            zeemanSplit,
            energyUnit,
        }
        collisionalCoefficient_balance = []

        collisionalCoefficient.forEach((coefficient) => {
            const { label, value } = coefficient
            const levelLabels = label.split(' --> ').map((f) => f.trim())

            let newLabel: string
            let newValue: number

            newValue = value * balance_distribution({ ...balanceArgs, label })
            newLabel = `${levelLabels[1]} --> ${levelLabels[0]}`

            const alreadyComputed = find(collisionalCoefficient, (rate) => rate.label == newLabel)
            if (!alreadyComputed) {
                collisionalCoefficient_balance = [
                    ...collisionalCoefficient_balance,
                    {
                        label: newLabel,
                        value: newValue.toExponential(3),
                        id: window.getID(),
                    },
                ]
            }
        })
    }

    const computeRate = (rate: ValueLabel) => {
        rate.value = Number(rate.value) * Number(numberDensity)
        rate.value = rate.value.toExponential(3)
        return rate
    }

    $: if (collisionalRateConstants.length > 0 && numberDensity) {
        collisionalRates = cloneDeep(collisionalRateConstants).map(computeRate)
    }

    let collisionalFileBasename = ''

    async function browse_collisional_file() {
        ;[collisionalFilename] = (await browse({ dir: false })) || collisionalFilename
        collisionalFileBasename = window.path.basename(collisionalFilename)
    }

    $: if (collisionalFilename) {
        collisionalFileBasename = window.path.basename(collisionalFilename)
    }

    let OpenRateConstantsPlot = false

    const saveCollisionalRateConstants = () => {
        const save_dir = window.path.dirname(collisionalCoefficientJSONFile)

        if (!window.fs.isDirectory(save_dir)) {
            return window.createToast(`Directory ${save_dir} does not exist`, 'danger')
        }

        const result = window.fs.outputJsonSync(collisionalCoefficientJSONFile, {
            collisionalCoefficient,
            collisionalCoefficient_balance,
        })

        if (window.fs.isError(result)) return window.handleError(result)
        console.log(`${collisionalCoefficientJSONFile} saved`)
        window.createToast('Saved: ' + window.path.basename(collisionalCoefficientJSONFile))
    }

    let collisionalCoefficientJSONFile = ''

    const readcollisionalCoefficientJSONFile = () => {
        if (!window.fs.isFile(collisionalCoefficientJSONFile)) return window.createToast('File not found', 'danger')
        console.log('loading: ', collisionalCoefficientJSONFile)
        const data = window.fs.readJsonSync(collisionalCoefficientJSONFile)
        if (window.fs.isError(data)) return window.handleError(data)
        ;({ collisionalCoefficient, collisionalCoefficient_balance } = data)

        if (window.db.get('active_tab') !== 'Kinetics') return
        window.createToast('loaded: ' + window.path.basename(collisionalCoefficientJSONFile), 'warning', {
            target: 'left',
        })
    }

    onMount(() => {
        const configLocation = <string>window.db.get('ROSAA_config_location') || ''
        if (!configLocation) return
        console.log(configLocation)
        collisionalCoefficientJSONFile = window.path.join(configLocation, 'files', 'collisionalCoefficients.json')
        readcollisionalCoefficientJSONFile()
    })
</script>

<CollisionalDistribution {...collisionalArgs} bind:active={collisionalWindow} />
<CollisionalRateConstantPlot
    {collisionalFilename}
    bind:active={OpenRateConstantsPlot}
    bind:collisionalCoefficient
    bind:collisionalTemp
/>

<!-- <CustomPanel label="Collisional rate constants" loaded={collisionalCoefficient.length > 0}> -->
<div class="align h-center">
    <button class="button is-link " on:click={compteCollisionalBalanceConstants}>Compute balance rate</button>
    <button class="button is-link " on:click={() => (collisionalWindow = true)}>Compute Collisional Cooling</button>
    <div class="align h-center">
        <button class="button is-link" on:click={browse_collisional_file}>Browse</button>
        <Textfield bind:value={collisionalFileBasename} label="collisionalFilename" disabled variant="outlined" />
        <Textfield bind:value={collisionalTemp} label="collisionalTemp" />
        <button class="button is-link" on:click={() => (OpenRateConstantsPlot = true)}>Compute rate constants</button>
        <button class="button is-link" on:click={readcollisionalCoefficientJSONFile}>Read</button>
        <button class="button is-link" on:click={saveCollisionalRateConstants}>Save</button>
    </div>
</div>

{#if collisionalCoefficient.length > 0}
    <div class="align h-center">
        {#each collisionalCoefficient as { label, value, id } (id)}
            <Textfield bind:value {label} />
        {/each}
    </div>
{/if}

{#if collisionalCoefficient_balance.length > 0}
    <hr />
    <div class="align h-center">
        {#each collisionalCoefficient_balance as { label, value, id } (id)}
            <Textfield bind:value {label} />
        {/each}
    </div>
{/if}

<hr />
<div class="align h-center subtitle">Collisional Rates (per sec)</div>
<div class="align h-center">
    <Textfield bind:value={numberDensity} label="numberDensity (cm-3)" />
</div>

<div class="align h-center">
    {#each collisionalRates as { label, value, id } (id)}
        <Textfield bind:value {label} />
    {/each}
</div>
