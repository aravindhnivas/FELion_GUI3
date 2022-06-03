<script>
    import { persistentWritable } from '$src/js/persistentStore'
    import ModalTable from '$components/ModalTable.svelte'
    import Textfield from '@smui/textfield'
    import CustomSelect from '$components/CustomSelect.svelte'
    export let loadConfig
    export let readConfigDir
    export let config_location = ''
    export let config_file = ''
    export let config_filelists = []
    export let configArray = []
    export let active = false

    let configKeys = ['filename', 'srgMode', 'pbefore', 'pafter', 'calibrationFactor', 'temp']

    const config_filename = persistentWritable('kinetics_config_filename', 'kinetics.config.json')

    // let config_filelists = []
    $: {
        config_file = window.path.join(config_location, $config_filename)
    }
    let config_content = {}

    function saveConfig() {
        if (!window.fs.existsSync(config_file)) {
            const [, error] = window.fs.outputJsonSync(config_file, config_content)
            if (error) {
                return window.handleError(error)
            }
        }
        const keys = configKeys.slice(1, configKeys.length)
        configArray.forEach((content) => {
            const filename = content['filename']
            const newKeyValue = {}
            keys.forEach((key) => {
                newKeyValue[key] = content[key]
            })
            config_content[filename] = newKeyValue
        })
        const [, error] = window.fs.outputJsonSync(config_file, config_content)
        if (error) {
            return window.handleError(error)
        }
        window.createToast('Config file saved' + window.path.basename(config_file), 'warning', { target: 'left' })
    }
</script>

<ModalTable
    bind:active
    title="Config table"
    bind:rows={configArray}
    keys={configKeys}
    userSelect={false}
    sortOption={true}
>
    <svelte:fragment slot="header">
        <div class="header">
            <Textfield value={window.path.dirname(config_file)} label="config location" disabled />

            <CustomSelect
                bind:value={$config_filename}
                label="config file (*.config.json)"
                options={config_filelists.filter((file) => file.endsWith('.config.json'))}
                update={readConfigDir}
            />
        </div>
    </svelte:fragment>

    <svelte:fragment slot="footer">
        <button class="button is-link" on:click={saveConfig}>Save</button>
        <button class="button is-warning" on:click={loadConfig}>Load</button>
        <button class="button is-danger" on:click={() => (active = false)}>Close</button>
    </svelte:fragment>
</ModalTable>

<style>
    .header {
        display: grid;
        gap: 1em;
        grid-auto-flow: column;
        grid-template-columns: 1fr auto;
        align-items: center;
    }
</style>
