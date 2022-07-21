<script>
    import { persistentWritable } from '$src/js/persistentStore'
    import Modal from '$components/modal/Modal.svelte'
    import STable from '$components/STable.svelte'
    export let configDir = ''
    export let active = false

    const configKeys = ['filename', 'srgMode', 'pbefore', 'pafter', 'C_factor', 'temp']
    const defaultRow = {
        filename: '',
        srgMode: '',
        pbefore: '',
        pafter: '',
        C_factor: '',
        temp: '',
    }

    const config_filename = persistentWritable('kinetics_config_filename', 'kinetics.configs.json')
    let config_datas = []
    const addNewRow = () => ({ ...defaultRow, id: window.getID() })
</script>

<Modal bind:active title="Kinetics config table" maxwidth="95vw" minheight="70vh">
    <svelte:fragment slot="content">
        <STable
            rowKeys={configKeys}
            bind:rows={config_datas}
            {configDir}
            options_filter={'.configs.json'}
            bind:filename={$config_filename}
            editable={true}
            sortable={true}
            closeableRows={true}
            fileReadProps={{ singleFilemode_ObjectKey: 'filename', uniqFilter: 'id' }}
        />
    </svelte:fragment>
    <svelte:fragment slot="footer">
        <button class="button is-warning" on:click={() => (config_datas = [...config_datas, addNewRow()])}
            >Add row</button
        >
    </svelte:fragment>
</Modal>
