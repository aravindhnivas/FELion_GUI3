<script>
    import { cloneDeep, find } from 'lodash-es'
    import Textfield from '@smui/textfield'
    import computePy_func from '$src/Pages/general/computePy'
    // import BoxComponent from './BoxComponent.svelte'
    import { PlanksConstant, SpeedOfLight } from '$src/js/constants'
    import { computeStatisticalWeight } from '../functions/balance_distribution'
    // import CustomPanel from '$components/CustomPanel.svelte'

    export let einsteinCoefficientA = []
    export let einsteinCoefficientB = []
    export let einsteinCoefficientB_rateConstant = []

    export let einsteinB_rateComputed = false
    export let lorrentz = 0.32
    export let gaussian = 0.21
    export let power = '2e-5'
    export let trapArea = '5e-5'
    export let energyUnit
    export let zeemanSplit
    export let energyLevels
    export let electronSpin

    async function computeEinsteinB() {
        try {
            console.log('Computing Einstein B constants', {
                einsteinCoefficientA,
                energyLevels,
            })
            einsteinB_rateComputed = false
            const einsteinCoefficientB_emission = einsteinCoefficientA.map(({ label, value }) => {
                const [final, initial] = label.split('-->').map((l) => l.trim())

                const v0 = find(energyLevels, (e) => e?.label == initial)?.value
                const v1 = find(energyLevels, (e) => e?.label == final)?.value

                const freq = parseFloat(v1) - parseFloat(v0)
                const freqInHz = energyUnit === 'MHz' ? freq * 1e6 : freq * SpeedOfLight * 100

                const constTerm = SpeedOfLight ** 3 / (8 * Math.PI * PlanksConstant * freqInHz ** 3)
                const B = constTerm * value

                return {
                    label,
                    value: B.toExponential(3),
                    id: window.getID(),
                }
            })

            const einsteinCoefficientB_absorption = einsteinCoefficientB_emission.map(({ label, value }) => {
                const [final, initial] = label.split('-->').map((l) => l.trim())

                const { Gi, Gf } = computeStatisticalWeight({
                    electronSpin,
                    zeemanSplit,
                    final,
                    initial,
                })
                const weight = Gf / Gi

                const B = weight * parseFloat(value)
                const newLabel = `${initial} --> ${final}`
                return {
                    label: newLabel,
                    value: B.toExponential(3),
                    id: window.getID(),
                }
            })

            einsteinCoefficientB = [...einsteinCoefficientB_emission, ...einsteinCoefficientB_absorption]
            einsteinCoefficientB_rateConstant = cloneDeep(einsteinCoefficientB)

            await computeRates()
        } catch (error) {
            window.handleError(error)
        }
    }

    let voigtline = ''

    async function computeRates(e) {
        if (einsteinCoefficientB.length < 1) return
        const lineshape = await computeLineshape(e)
        if (!lineshape) return
        voigtline = lineshape

        const constantTerm = parseFloat(power) / (parseFloat(trapArea) * SpeedOfLight)
        const norm = constantTerm * parseFloat(voigtline)

        einsteinCoefficientB = einsteinCoefficientB_rateConstant.map((rateconstant) => ({
            ...rateconstant,
            value: Number(rateconstant.value * norm).toExponential(3),
        }))
        einsteinB_rateComputed = einsteinCoefficientB.length > 0
    }

    let computing_lineshape = false
    async function computeLineshape(e = null) {
        if (computing_lineshape) return
        if (!lorrentz || !gaussian) return createToast('Compute gaussian and lorrentz parameters')
        computing_lineshape = true
        const dataFromPython = await computePy_func({
            e,
            pyfile: 'ROSAA.voigt',
            args: { lorrentz, gaussian },
        })
        computing_lineshape = false
        if (!dataFromPython) return
        const lineshape = dataFromPython?.lineShape?.toExponential(2)
        return lineshape
    }

    $: if (einsteinCoefficientA.length) {
        computeEinsteinB()
    }
</script>

<div class="align h-center subtitle">Einstein A Co-efficients</div>

<div class="align h-center mb-5">
    {#if einsteinCoefficientA.length > 0}
        {#each einsteinCoefficientA as { label, value, id } (id)}
            <Textfield bind:value {label} />
        {/each}
    {/if}
</div>

<div class="align h-center ">
    <button class="button is-link" on:click={computeEinsteinB}>
        {#if einsteinCoefficientB.length < 1}
            <i class="material-icons">sync_problem</i>
        {/if}
        Compute Einstein B
    </button>
</div>

{#if einsteinCoefficientB.length > 0}
    <hr />

    <div class="align h-center subtitle">Einstein B Co-efficients</div>
    <div class="align h-center">
        <Textfield bind:value={voigtline} label="voigt lineshape (Hz)" />
        <button class="button is-link " on:click={computeRates}>
            {#if !einsteinB_rateComputed}
                <i class="material-icons">sync_problem</i>
            {/if}
            Compute rate constants
        </button>
    </div>

    <div class="align h-center">
        {#each einsteinCoefficientB as { label, value, id } (id)}
            <Textfield bind:value {label} />
        {/each}
    </div>
{/if}
