<script lang="ts">
    import Textfield from '@smui/textfield'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'
    import CustomPanel from '$components/CustomPanel.svelte'
    import type { totalMassKeyType } from '$src/Pages/timescan/types/types'
    export let legends = ''
    export let useParamsFile = false
    export let loaded = false
    export let nameOfReactants = ''
    // export let config_filelists = []
    // export let kinetics_params_file = ''
    export let totalMassKey: totalMassKeyType = []

    // export let updateParamsFile = () => {}
    export let computeOtherParameters = (_?: boolean): void => {}
    // export let configDir
</script>

<CustomPanel label="Labels" style="display: flex; flex-direction: column; gap: 1em;" {loaded}>
    <!-- <div class="align" style="align-items: flex-end; justify-content: flex-end">
        <button class="button is-warning" on:click={() => computeOtherParameters()}>load</button>
        <TextAndSelectOptsToggler
            bind:value={kinetics_params_file}
            label="fit-config file (*.params.json)"
            lookFor=".params.json"
            lookIn={configDir}
        />
        <button class="button is-link" on:click={updateParamsFile}>update</button>
    </div> -->

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
                    on:click={() => {
                        useParamsFile = false
                        included = !included
                        computeOtherParameters()
                    }}
                />
            </span>
        {/each}
    </div>

    {#if totalMassKey.filter((m) => m.included).length < 2}
        <span class="tag is-danger"> atleast two reactants are required for kinetics </span>
    {/if}
</CustomPanel>
