<script>
    import ModalTable from '$components/ModalTable.svelte'
    import Textfield from '@smui/textfield'
    export let config_file = ''
    export let configArray = []
    export let active = false

    let configKeys = [
        'filename',
        'srgMode',
        'pbefore',
        'pafter',
        'calibrationFactor',
        'temp',
    ]
    let config_file_ROSAAkinetics = 'config_file_ROSAAkinetics.json'
    let config_content = {}

    function saveConfig() {
        if (!fs.existsSync(config_file)) {
            return window.createToast('Invalid location or filename', 'danger')
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
        // const config_file = pathJoin(config_file, config_file_ROSAAkinetics);
        fs.outputJsonSync(config_file, config_content)
        window.createToast(
            'Config file saved' + config_file_ROSAAkinetics,
            'warning'
        )
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
        <div class="align">
            <Textfield
                value={config_file}
                label="config location"
                disabled
                style="width: 100%; border: solid 1px #fff7;"
            />
        </div>
    </svelte:fragment>
    <svelte:fragment slot="footer">
        <button class="button is-link" on:click={saveConfig}>Save</button>
        <button class="button is-danger" on:click={() => (active = false)}
            >Close</button
        >
    </svelte:fragment>
</ModalTable>
