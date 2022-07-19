<script lang="ts">
    import Textfield from '@smui/textfield'
    import CustomPanel from '$components/CustomPanel.svelte'
    import type { totalMassKeyType } from '$src/Pages/timescan/types/types'
    import { tick } from 'svelte'
    export let legends = ''
    export let useParamsFile = false
    export let loaded = false
    export let nameOfReactants = ''
    export let totalMassKey: totalMassKeyType = []
    export let computeOtherParameters = (_?: boolean): void => {}
</script>

<CustomPanel label="Labels" style="display: flex; flex-direction: column; gap: 1em;" {loaded}>
    <slot name="basic-infos" />
    <div class="align h-center">
        <Textfield bind:value={nameOfReactants} label="nameOfReactants" style="width:30%" />
        <Textfield bind:value={legends} label="legends" style="width:30%" />
    </div>

    <div class="align h-center">
        {#each totalMassKey as { mass, id, included } (id)}
            <span class="tag is-warning" class:is-danger={!included}>
                {mass}
                <button
                    class="delete is-small"
                    on:click={async () => {
                        useParamsFile = false
                        included = !included
                        await tick()
                        computeOtherParameters()
                        await tick()
                    }}
                />
            </span>
        {/each}
    </div>
    {#if totalMassKey.filter((m) => m.included).length < 2}
        <span class="tag is-danger"> atleast two reactants are required for kinetics </span>
    {/if}
    <slot name="rate-constants" />
</CustomPanel>
