<script>
    import Modal from './Modal.svelte'
    import Textfield from '@smui/textfield'
    import CustomSelect from './CustomSelect.svelte'
    import CustomSwitch from './CustomSwitch.svelte'
    import settings_key_value_infos from '$src/settings_key_value_infos.json'
    import get_files_settings_values from '$src/js/get_files_settings_values'

    export let currentLocation = ''
    export let fullfileslist = []
    export let fileChecked = []
    export let active = false

    const style = 'width:14em; height:3.5em; margin-right:0.5em'
    let showAllFiles = true
    let selected_file = ''
    $: displayFiles = showAllFiles ? fullfileslist : fileChecked
    $: loadfilename = pathJoin(currentLocation, selected_file)
</script>

<button
    class="button is-link"
    on:click={() => {
        active = true
    }}>GetLabviewSettings</button
>

{#if active}
    <Modal title="Labview Settings" bind:active>
        <svelte:fragment slot="body_header__div">
            <div class="controller">
                <CustomSwitch bind:selected={showAllFiles} label="show all" />
                <CustomSelect
                    auto_init={true}
                    bind:value={selected_file}
                    label="Filename"
                    options={displayFiles}
                />
            </div>
        </svelte:fragment>

        <svelte:fragment slot="body_scrollable__div">
            {#await get_files_settings_values(loadfilename)}
                <div class="info-box">loading...</div>
            {:then variableValues}
                <div class="container">
                    {#each Object.keys(settings_key_value_infos) as id (id)}
                        <div style:margin-bottom="2rem">
                            <h1>{id}</h1>
                            <div>
                                {#each settings_key_value_infos[id] as key}
                                    <Textfield
                                        {style}
                                        value={variableValues[key] ?? ''}
                                        label={key}
                                        type="number"
                                        disabled
                                    />
                                {/each}
                            </div>
                        </div>
                    {/each}
                </div>
            {:catch error}
                <div class="info-box error" style:background="#f14668">
                    {error}
                </div>
            {/await}
        </svelte:fragment>
    </Modal>
{/if}

<style>
    .info-box {
        display: flex;
        margin-top: 1em;

        padding: 1em;
        justify-content: center;
    }
    .controller {
        display: flex;
        gap: 1em;
    }
    .container {
        display: grid;
        padding: 1em;
        height: 90%;
        overflow-y: auto;
    }
</style>
