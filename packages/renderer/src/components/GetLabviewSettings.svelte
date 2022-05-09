<script>
    import Modal from './Modal.svelte'
    import Textfield from '@smui/textfield'
    import CustomSelect from './CustomSelect.svelte'
    import CustomSwitch from './CustomSwitch.svelte'
    import settings_key_value_infos from '$src/settings_key_value_infos.json'

    export let currentLocation = ''
    export let fullfileslist = []
    export let fileChecked = []
    export let active = false

    const style = 'width:14em; height:3.5em; margin-right:0.5em'
    const validate_line = (line) => {
        const valid =
            line.trim().length > 0 && line.startsWith('# Sect01 Ion Source')
        return valid
    }

    const get_settings_value = (selected_file) => {
        return new Promise(async (resolve, reject) => {
            if (!selected_file) return reject('No file selected')

            const filename = pathJoin(currentLocation, selected_file)
            if (!fs.existsSync(filename))
                return reject(`${filename} does not exist`)

            const [fileContents, error] = await fs.readFile(filename)
            if (error) return reject(error)

            const variableValues = {}
            for (const line of fileContents.split('\n')) {
                if (!validate_line(line)) continue
                const keyValuesLine = line.split(' ')
                const key = keyValuesLine[7]
                const value = keyValuesLine[9]
                variableValues[key] = value
            }
            return resolve(variableValues)
        })
    }

    let showAllFiles = true
    let selected_file = ''
    $: displayFiles = showAllFiles ? fullfileslist : fileChecked
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
                    bind:picked={selected_file}
                    label="Filename"
                    options={displayFiles}
                />
            </div>
        </svelte:fragment>

        <svelte:fragment slot="body_scrollable__div">
            {#await get_settings_value(selected_file)}
                <div class="info-box">loading...</div>
            {:then variableValues}
                <div class="container">
                    {#each Object.keys(settings_key_value_infos) as id (id)}
                        <div class="row">
                            <h1>{id}</h1>
                            <div class="row-contents">
                                {#each settings_key_value_infos[id] as key}
                                    <Textfield
                                        {style}
                                        value={variableValues[key] ?? ''}
                                        label={key}
                                        disabled
                                    />
                                {/each}
                            </div>
                        </div>
                    {/each}
                </div>
            {:catch error}
                <div class="info-box error">{error}</div>
            {/await}
        </svelte:fragment>
    </Modal>
{/if}

<style>
    .info-box {
        display: flex;
        margin-top: 1em;
        justify-content: center;
        padding: 1em;
    }
    .error {
        background: #f14668;
    }
    .controller {
        display: flex;
        gap: 1em;
    }
    .row {
        margin-bottom: 2em;
    }
    .container {
        display: grid;
        padding: 1em;
        height: 90%;
        overflow-y: auto;
    }
</style>
