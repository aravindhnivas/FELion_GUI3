<script>
    import Textfield from '@smui/textfield'
    import TextAndSwitchToggler from '$src/components/TextAndSwitchToggler.svelte'
    import CustomSwitch from '$src/components/CustomSwitch.svelte'
    import { fade } from 'svelte/transition'
    export let totalMassKey = []
    export let nameOfReactants = ''
    export let legends = ''
    export let useParamsFile = false
    export let params_found = false
    export let updateParamsFile = () => {}
    export let kinetics_params_file = ''
    export let config_filelists = []
    export let selectedFile = ''
    export let computeOtherParameters = () => {}
    export let readConfigDir = () => {}
</script>

<div class="align box h-center" style:flex-direction="column">
    <div class="align h-center">
        <Textfield
            bind:value={nameOfReactants}
            label="nameOfReactants"
            style="width:30%"
        />

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
        <span class="tag is-danger">
            atleast two reactants are required for kinetics
        </span>
    {/if}

    <div class="align h-center">
        <CustomSwitch
            on:change={computeOtherParameters}
            bind:selected={useParamsFile}
            label="use params file"
        />

        <TextAndSwitchToggler
            bind:value={kinetics_params_file}
            label="fit-config file (*.params.json)"
            options={config_filelists.filter((f) => f.endsWith('.params.json'))}
            update={readConfigDir}
        />

        <button class="button is-link" on:click={computeOtherParameters}
            >read</button
        >
        <button class="button is-link" on:click={updateParamsFile}
            >update</button
        >
        {#if useParamsFile && selectedFile}
            <span
                class="tag is-success"
                class:is-danger={!params_found}
                transition:fade
                >{params_found
                    ? `params updated: ${window.basename(selectedFile)}`
                    : 'params not found'}</span
            >
        {/if}
    </div>
</div>

<style>
    .box {
        margin: 0;
        padding: 0.5em;
        border: solid 1px #fff7;
    }
</style>
