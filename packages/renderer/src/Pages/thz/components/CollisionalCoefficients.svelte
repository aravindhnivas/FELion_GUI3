<script lang="ts">
    import {
        collisionalCoefficient_balance,
        collisionalCoefficient,
        collisionalRates,
        collisionalRateConstants,
    } from '../stores/collisional'
    import { numberDensity, collisionalTemp, configLoaded } from '../stores/common'
    import BrowseTextfield from '$src/components/BrowseTextfield.svelte'
    import Textfield from '@smui/textfield'
    import { find, cloneDeep, isEmpty } from 'lodash-es'
    import { onMount, tick } from 'svelte'

    import balance_distribution from '../functions/balance_distribution'
    import CollisionalDistribution from '../windows/CollisionalDistribution.svelte'
    import CollisionalRateConstantPlot from '../windows/CollisionalRateConstantPlot.svelte'
    import CustomPanel from '$src/components/CustomPanel.svelte'

    export let collisionalFilename = ''

    let activate_collisional_simulation_window = false

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

    const readcollisionalCoefficientJSONFile = (toast = true) => {
        if (!window.fs.isFile(collisionalCoefficientJSONFile)) {
            if (!toast) return console.warn(`${collisionalCoefficientJSONFile} does not exist`)
            return window.createToast('File not found', 'danger')
        }

        console.log('loading: ', collisionalCoefficientJSONFile)
        const data = window.fs.readJsonSync(collisionalCoefficientJSONFile)
        if (window.fs.isError(data)) return window.handleError(data)

        if (isEmpty(data)) return window.createToast('Collisional data file is empty', 'danger')
        ;({ $collisionalCoefficient, $collisionalCoefficient_balance } = data)

        if (window.db.get('active_tab') !== 'Kinetics') return

        window.createToast('loaded: ' + window.path.basename(collisionalCoefficientJSONFile), 'warning', {
            target: 'left',
        })
    }

    const after_configs_loaded = async () => {
        await tick()
        readcollisionalCoefficientJSONFile()
    }
    $: if ($configLoaded) {
        after_configs_loaded()
    }
</script>

<CollisionalDistribution bind:active={activate_collisional_simulation_window} />
<CollisionalRateConstantPlot {collisionalFilename} bind:active={OpenRateConstantsPlot} />

<CustomPanel
    label="Collisional rate constants"
    loaded={$numberDensity.length > 0 && $collisionalRateConstants.length > 0}
>
    <div class="align h-center">
        <div class="align h-center">
            <BrowseTextfield
                dir={false}
                filetype="txt"
                class="three_col_browse"
                bind:value={collisionalFilename}
                label="collisionalFilename"
                lock={true}
                on:fileupdate={(e) => {
                    console.log(e)
                }}
            >
                <button class="button is-warning" on:click={() => readcollisionalCoefficientJSONFile()}>load</button>
                <button class="button is-link" on:click={saveCollisionalRateConstants}>Save</button>
            </BrowseTextfield>

            <Textfield bind:value={$collisionalTemp} label="collisionalTemp" />
            <button class="button is-warning" on:click={() => (OpenRateConstantsPlot = true)}
                >Derive rate from fit</button
            >

            <button class="button is-link " on:click={compteCollisionalBalanceConstants}>Compute balance rate</button>
            <button class="button is-link flex" on:click={() => (activate_collisional_simulation_window = true)}>
                <span>Simulate Collisional Cooling</span><span class="material-symbols-outlined">open_in_full</span>
            </button>
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
