<script lang="ts">
    import {
        collisionalCoefficient_balance,
        collisionalCoefficient,
        collisionalRates,
        collisionalRateConstants,
    } from '../stores/collisional'
    import { numberDensity, collisionalTemp } from '../stores/common'
    import BrowseTextfield from '$src/components/BrowseTextfield.svelte'
    import Textfield from '@smui/textfield'
    import { find, cloneDeep } from 'lodash-es'
    import { onMount } from 'svelte'
    import balance_distribution from '../functions/balance_distribution'
    import CollisionalDistribution from '../windows/CollisionalDistribution.svelte'
    import CollisionalRateConstantPlot from '../windows/CollisionalRateConstantPlot.svelte'
    import CustomPanel from '$src/components/CustomPanel.svelte'

    export let collisionalFilename = ''

    let collisionalWindow = false

    const compteCollisionalBalanceConstants = () => {
        $collisionalCoefficient_balance = []

        $collisionalCoefficient.forEach((coefficient) => {
            const { label, value } = coefficient
            const levelLabels = label.split(' --> ').map((f) => f.trim())

            const balance = balance_distribution({ collisionalTemp: $collisionalTemp, label })
            if (balance === null) return

            const newValue = Number(value) * balance
            const newLabel = `${levelLabels[1]} --> ${levelLabels[0]}`

            const alreadyComputed = find($collisionalCoefficient, (rate) => rate.label == newLabel)
            if (!alreadyComputed) {
                $collisionalCoefficient_balance = [
                    ...$collisionalCoefficient_balance,
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
        const value = Number(rate.value) * Number($numberDensity)
        rate.value = value.toExponential(3)
        return rate
    }

    $: if ($collisionalRateConstants.length > 0 && $numberDensity) {
        $collisionalRates = cloneDeep($collisionalRateConstants).map(computeRate)
    }

    let OpenRateConstantsPlot = false

    const saveCollisionalRateConstants = () => {
        const save_dir = window.path.dirname(collisionalCoefficientJSONFile)

        if (!window.fs.isDirectory(save_dir)) {
            return window.createToast(`Directory ${save_dir} does not exist`, 'danger')
        }
        // console.log(save_dir)
        const result = window.fs.outputJsonSync(collisionalCoefficientJSONFile, {
            $collisionalCoefficient,
            $collisionalCoefficient_balance,
        })

        if (window.fs.isError(result)) return window.handleError(result)
        console.log(`${collisionalCoefficientJSONFile} saved`)
        window.createToast('Saved: ' + window.path.basename(collisionalCoefficientJSONFile))
    }

    $: configFileDir = window.path.dirname(collisionalFilename)
    $: collisionalCoefficientJSONFile = window.path.join(configFileDir, 'collisionalCoefficients.json')

    const readcollisionalCoefficientJSONFile = () => {
        if (!window.fs.isFile(collisionalCoefficientJSONFile)) return window.createToast('File not found', 'danger')
        console.log('loading: ', collisionalCoefficientJSONFile)
        const data = window.fs.readJsonSync(collisionalCoefficientJSONFile)
        if (window.fs.isError(data)) return window.handleError(data)
        ;({
            collisionalCoefficient: $collisionalCoefficient,
            collisionalCoefficient_balance: $collisionalCoefficient_balance,
        } = data)

        if (window.db.get('active_tab') !== 'Kinetics') return
        window.createToast('loaded: ' + window.path.basename(collisionalCoefficientJSONFile), 'warning', {
            target: 'left',
        })
    }

    onMount(() => {
        if (!window.fs.isFile(collisionalCoefficientJSONFile)) return
        readcollisionalCoefficientJSONFile()
    })
</script>

<CollisionalDistribution bind:active={collisionalWindow} />
<CollisionalRateConstantPlot {collisionalFilename} bind:active={OpenRateConstantsPlot} />

<CustomPanel label="Collisional rate constants" loaded={$collisionalRateConstants.length > 0}>
    <div class="align h-center">
        <button class="button is-link " on:click={compteCollisionalBalanceConstants}>Compute balance rate</button>
        <button class="button is-link " on:click={() => (collisionalWindow = true)}>Compute Collisional Cooling</button>
        <div class="align h-center">
            <BrowseTextfield
                dir={false}
                filetype="txt"
                class="three_col_browse"
                bind:value={collisionalFilename}
                label="collisionalFilename"
                lock={true}
            />
            <Textfield bind:value={$collisionalTemp} label="collisionalTemp" />
            <button class="button is-link" on:click={() => (OpenRateConstantsPlot = true)}
                >Compute rate constants</button
            >
            <button class="button is-link" on:click={readcollisionalCoefficientJSONFile}>Read</button>
            <button class="button is-link" on:click={saveCollisionalRateConstants}>Save</button>
        </div>
    </div>

    {#if $collisionalCoefficient.length > 0}
        <div class="align h-center">
            {#each $collisionalCoefficient as { label, value, id } (id)}
                <Textfield bind:value {label} />
            {/each}
        </div>
    {/if}

    {#if $collisionalCoefficient_balance.length > 0}
        <hr />
        <div class="align h-center">
            {#each $collisionalCoefficient_balance as { label, value, id } (id)}
                <Textfield bind:value {label} />
            {/each}
        </div>
    {/if}

    <hr />
    <div class="align h-center subtitle">Collisional Rates (per sec)</div>
    <div class="align h-center">
        <Textfield bind:value={$numberDensity} label="numberDensity (cm-3)" />
    </div>
    <div class="align h-center">
        {#each $collisionalRates as { label, value, id } (id)}
            <Textfield bind:value {label} />
        {/each}
    </div>
</CustomPanel>
