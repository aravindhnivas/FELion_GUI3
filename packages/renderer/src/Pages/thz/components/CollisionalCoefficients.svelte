<script>
    import Textfield from '@smui/textfield'
    import { find, cloneDeep } from 'lodash-es'
    import { onMount } from 'svelte'
    import balance_distribution from '../functions/balance_distribution'
    import CollisionalDistribution from '../windows/CollisionalDistribution.svelte'
    import CollisionalRateConstantPlot from '../windows/CollisionalRateConstantPlot.svelte'
    import BoxComponent from './BoxComponent.svelte'
    import { browse } from '$components/Layout.svelte'

    export let energyUnit
    export let zeemanSplit
    export let energyLevels
    export let electronSpin
    export let numberOfLevels

    export let numberDensity = '4e14'
    export let collisionalRates = []
    export let collisionalTemp
    export let collisionalFilename = ''
    export let collisionalCoefficient = []
    export let collisionalCoefficient_balance = []

    let collisionalWindow = false
    $: collisionalRateConstants = [
        ...collisionalCoefficient,
        ...collisionalCoefficient_balance,
    ]
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
            let newLabel, newValue
            newValue = value * balance_distribution({ ...balanceArgs, label })
            newLabel = `${levelLabels[1]} --> ${levelLabels[0]}`

            const alreadyComputed = find(
                collisionalCoefficient,
                (rate) => rate.label == newLabel
            )
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

    const computeRate = (rate) => {
        rate.value *= numberDensity
        rate.value = rate.value.toExponential(3)
        return rate
    }

    $: if (collisionalRateConstants.length > 0 && numberDensity) {
        collisionalRates = cloneDeep(collisionalRateConstants).map(computeRate)
    }

    let collisionalFileBasename = ''
    async function browse_collisional_file() {
        ;[collisionalFilename] =
            (await browse({ dir: false })) || collisionalFilename
        collisionalFileBasename = window.path.basename(collisionalFilename)
    }

    const updateFilename = async () => {
        collisionalFileBasename = window.path.basename(collisionalFilename)
    }

    $: if (collisionalFilename) updateFilename()
    let OpenRateConstantsPlot = false

    const saveCollisionalRateConstants = () => {
        const [, error] = window.fs.outputJsonSync(
            collisionalCoefficientJSONFile,
            {
                collisionalCoefficient,
                collisionalCoefficient_balance,
            }
        )
        if (error) {
            return window.handleError(error)
        }

        window.createToast('Saved: ' + collisionalCoefficientJSONFile)
    }

    let collisionalCoefficientJSONFile = ''

    const readcollisionalCoefficientJSONFile = () => {
        if (window.fs.existsSync(collisionalCoefficientJSONFile)) {
            console.log('loading: ', collisionalCoefficientJSONFile)
            ;[{ collisionalCoefficient, collisionalCoefficient_balance }] =
                window.fs.readJsonSync(collisionalCoefficientJSONFile)
            if (window.db.get('active_tab') == 'Kinetics') {
                window.createToast(
                    'loaded: ' +
                        window.path.basename(collisionalCoefficientJSONFile),
                    'warning',
                    { target: 'left' }
                )
            }
        }
    }

    onMount(() => {
        const configLocation = window.db.get('ROSAA_config_location') || ''
        if (!configLocation) return
        console.log(configLocation)
        collisionalCoefficientJSONFile = window.path.join(
            configLocation,
            'files',
            'collisionalCoefficients.json'
        )
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

<BoxComponent
    title="Collisional rate constants"
    loaded={collisionalCoefficient.length > 0}
>
    <svelte:fragment slot="control">
        <button
            class="button is-link "
            on:click={compteCollisionalBalanceConstants}
            >Compute balance rate</button
        >
        <button
            class="button is-link "
            on:click={() => (collisionalWindow = true)}
            >Compute Collisional Cooling</button
        >

        <div class="align h-center">
            <button class="button is-link" on:click={browse_collisional_file}
                >Browse</button
            >
            <Textfield
                bind:value={collisionalFileBasename}
                label="collisionalFilename"
                disabled
                variant="outlined"
            />
            <Textfield bind:value={collisionalTemp} label="collisionalTemp" />
            <button
                class="button is-link"
                on:click={() => (OpenRateConstantsPlot = true)}
                >Compute rate constants</button
            >
            <button
                class="button is-link"
                on:click={readcollisionalCoefficientJSONFile}>Read</button
            >
            <button
                class="button is-link"
                on:click={saveCollisionalRateConstants}>Save</button
            >
        </div>
    </svelte:fragment>

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
</BoxComponent>
