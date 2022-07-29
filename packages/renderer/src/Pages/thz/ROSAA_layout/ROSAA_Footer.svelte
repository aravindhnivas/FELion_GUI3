<script lang="ts">
    import ButtonBadge from '$components/ButtonBadge.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import { tick } from 'svelte'

    export let progress = 0
    export let showreport = false
    export let statusReport = ''
    export let simulationMethod = 'Normal'
    export let simulation: (e?: Event) => Promise<void>
    const simulationMethods = ['Normal', 'FixedPopulation', 'withoutCollisionalConstants']
</script>

<button
    style="align-self:end;"
    class="button is-danger"
    class:hide={!showreport}
    on:click={() => {
        statusReport = ''
    }}>clear</button
>
<button
    style="align-self:end;"
    class="button is-warning"
    on:click={() => {
        showreport = !showreport
    }}>{showreport ? 'Go back' : 'Show progress'}</button
>
<div style="display: flex; gap: 1em;" class:hide={showreport}>
    <CustomSelect options={simulationMethods} bind:value={simulationMethod} label="simulationMethod" />
    <ButtonBadge
        on:pyEventData={async (e) => {
            const { stdout } = e.detail
            statusReport += stdout
            if (stdout.includes('%')) {
                const percent = parseFloat(stdout.split('%')[0].trim())
                if (percent > 0) {
                    progress = percent / 100
                }
            }
            await tick()
            document.getElementById('THz_simulation_status').scrollIntoView(false)
        }}
        on:click={(simulation ??= () => {
            console.log('simulation not set')
        })}
        style="align-self:end;"
    />
</div>
