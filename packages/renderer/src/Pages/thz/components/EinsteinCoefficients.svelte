<script lang="ts">
    import { energyUnit, energyLevels } from '../stores/energy'
    import { einsteinCoefficientA, einsteinCoefficientB, einsteinCoefficientB_rateConstant } from '../stores/einstein'
    import { trapArea, configLoaded } from '../stores/common'
    import { cloneDeep, find, isArray } from 'lodash-es'
    import Textfield from '@smui/textfield'
    import computePy_func from '$src/Pages/general/computePy'
    import { PlanksConstant, SpeedOfLight } from '$src/js/constants'
    import { computeStatisticalWeight } from '../functions/balance_distribution'
    import CustomPanel from '$src/components/CustomPanel.svelte'
    import BrowseTextfield from '$src/components/BrowseTextfield.svelte'
    import { correctObjValue, getYMLFileContents, setID } from '$src/js/utils'
    import { tick } from 'svelte'
    import Clipboard from 'svelte-clipboard'
    import { makeTable, formatNumber } from '../functions/utils'

    export let lorrentz = 0.32
    export let gaussian = 0.21
    export let power: string | number = '2e-5'
    export let einsteinFilename: string = ''
    export let moleculeName = ''
    // export let tagName = ''

    let einsteinB_rateComputed = false

    async function computeEinsteinB() {
        try {
            console.log('Computing Einstein B constants', {
                $einsteinCoefficientA,
                $energyLevels,
            })
            einsteinB_rateComputed = false
            const einsteinCoefficientB_emission = $einsteinCoefficientA.map(({ label, value }) => {
                const [final, initial] = label.split('-->').map((l) => l.trim())

                const v0 = find($energyLevels, (e) => e?.label == initial)?.value ?? 0
                const v1 = find($energyLevels, (e) => e?.label == final)?.value ?? 0

                const freq = Number(v1) - Number(v0)
                const freqInHz = $energyUnit === 'MHz' ? freq * 1e6 : freq * SpeedOfLight * 100

                const constTerm = SpeedOfLight ** 3 / (8 * Math.PI * PlanksConstant * freqInHz ** 3)
                const B = constTerm * +value

                return {
                    label,
                    value: B.toExponential(3),
                    id: window.getID(),
                }
            })

            const einsteinCoefficientB_absorption = einsteinCoefficientB_emission.map(({ label, value }) => {
                const [final, initial] = label.split('-->').map((l) => l.trim())

                const { Gi, Gf } = computeStatisticalWeight({
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

            $einsteinCoefficientB = [...einsteinCoefficientB_emission, ...einsteinCoefficientB_absorption]
            $einsteinCoefficientB_rateConstant = cloneDeep($einsteinCoefficientB)
            console.log({ $einsteinCoefficientB, $einsteinCoefficientB_rateConstant })
            await computeRates()
        } catch (error) {
            window.handleError(error)
        }
    }

    let voigtline = ''

    async function computeRates(e?: Event) {
        if ($einsteinCoefficientB.length < 1) return
        const lineshape = await computeLineshape(e)
        if (!lineshape) return
        voigtline = lineshape

        const constantTerm = Number(power) / (Number($trapArea) * SpeedOfLight)
        const norm = constantTerm * parseFloat(voigtline)

        console.log({ $einsteinCoefficientB_rateConstant, norm })

        $einsteinCoefficientB = $einsteinCoefficientB_rateConstant.map((rateconstant) => ({
            ...rateconstant,
            value: Number(+rateconstant.value * norm).toExponential(3),
        }))

        einsteinB_rateComputed = $einsteinCoefficientB.length > 0
    }

    let computing_lineshape = false

    async function computeLineshape(e?: Event) {
        if (!$configLoaded) return
        if (computing_lineshape) return

        console.log({ lorrentz, gaussian })
        if (!(lorrentz > 0)) {
            if (e) {
                window.createToast('Invalid Lorrentz parameters', 'danger')
            }
            return
        }
        if (!(gaussian > 0)) {
            if (e) {
                window.createToast('Invalid Gaussian parameters', 'danger')
            }
            return
        }

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

    $: if ($einsteinCoefficientA.length) {
        computeEinsteinB()
    }

    const loadfile = async () => {
        if (!window.fs.isFile(einsteinFilename)) return window.createToast('File not found', 'danger')
        const data = await getYMLFileContents(einsteinFilename)
        if (!isArray(data?.rateConstants)) return window.createToast('EinsteinA - Invalid file format', 'danger')
        $einsteinCoefficientA = data.rateConstants.map(setID).map(correctObjValue)
    }

    const after_configs_loaded = async () => {
        await tick()
        loadfile()
    }
    $: if ($configLoaded) {
        after_configs_loaded()
    }

    let fullTable = ''

    const copyAsTeXTable = () => {
        const caption = `Derived radiative rates at P=${formatNumber(
            power
        )} W, ${moleculeName} ion for an initial $|i\\rangle$ state transitions into final $|j\\rangle$ state with $A_{ij}$ spontaneous emission, $B_{ij}$ stimulated absorption and $B_{ji}$ stimulated emission. All $A_{ij}$, $B_{ij}$ and $B_{ji}$ are in units of s$^{-1}$.`

        const label = `tab:radiative-rate-coefficients`

        const levels = $einsteinCoefficientA.map((e) => e.label)
        let body = ''

        for (const level of levels) {
            const [from, to] = level.split('-->')
            body += `\n\t\t${from.trim()} & ${to.trim()} & `

            const A_val = find($einsteinCoefficientA, (e) => e.label == level)?.value

            const B_val = find($einsteinCoefficientB, (e) => e.label == level)?.value
            const B_balance = find($einsteinCoefficientB, (e) => e.label == `${to.trim()} --> ${from.trim()}`)?.value
            console.log({ A_val, B_val, B_balance })
            if (A_val && B_val && B_balance) {
                body += `${formatNumber(A_val)} & ${formatNumber(B_val)} & ${formatNumber(B_balance)} \\\\`
            }
        }
        const column_align = 'rclll'
        const header = `i & j & $A_{ij}$ & $B_{ij}$ & $B_{ji}$`

        fullTable = makeTable(caption, label, column_align, header, body)
    }
</script>

<CustomPanel label="Einstein Co-efficients" loaded={einsteinB_rateComputed}>
    <div class="align h-center subtitle">Einstein A Co-efficients</div>

    <BrowseTextfield
        dir={false}
        filetype="yml"
        class="three_col_browse"
        bind:value={einsteinFilename}
        label="filename"
        lock={true}
    >
        <button class="button is-warning" on:click={loadfile}>load</button>
    </BrowseTextfield>

    <div class="align h-center mb-5">
        {#if $einsteinCoefficientA.length > 0}
            {#each $einsteinCoefficientA as { label, value, id } (id)}
                <Textfield bind:value {label} />
            {/each}
        {/if}
    </div>

    <div class="align h-center ">
        <button class="button is-link" class:is-loading={computing_lineshape} on:click={computeEinsteinB}>
            {#if $einsteinCoefficientB.length < 1}
                <i class="material-symbols-outlined">sync_problem</i>
            {/if}
            Compute Einstein B
        </button>

        <Clipboard
            text={fullTable}
            let:copy
            on:copy={() => {
                window.createToast('Copied to clipboard', 'success')
            }}
        >
            <button
                class="button is-warning"
                on:click={async () => {
                    copyAsTeXTable()
                    await tick()
                    copy()
                }}>copy as TeXTable</button
            >
        </Clipboard>
    </div>

    {#if $einsteinCoefficientB.length > 0}
        <hr />

        <div class="align h-center subtitle">Einstein B Co-efficients</div>
        <div class="align h-center">
            <Textfield bind:value={voigtline} label="voigt lineshape (Hz)" />
            <button class="button is-link " on:click={computeRates}>
                {#if !einsteinB_rateComputed}
                    <i class="material-symbols-outlined">sync_problem</i>
                {/if}
                Compute rate constants
            </button>
        </div>

        <div class="align h-center">
            {#each $einsteinCoefficientB as { label, value, id } (id)}
                <Textfield bind:value {label} />
            {/each}
        </div>
    {/if}
</CustomPanel>
