<script>
    import { persistentWritable } from '$src/js/persistentStore'
    import { onMount, tick } from 'svelte'
    import { fade } from 'svelte/transition'
    import { cloneDeep } from 'lodash-es'
    import Textfield from '@smui/textfield'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import LayoutDiv from '$components/LayoutDiv.svelte'
    import computePy_func from '$src/Pages/general/computePy'
    import KineticConfigTable from './KineticConfigTable.svelte'

    import KineticEditor from './KineticEditor.svelte'
    import MatplotlibDialog from './MatplotlibDialog.svelte'
    import { browse } from '$components/Layout.svelte'

    let currentLocation = window.db.get('kinetics_location') || ''

    let timestartIndexScan = 0
    let fileCollections = []
    let srgMode = true
    let pbefore = 0
    let pafter = 0
    let temp = 5
    let molecule = 'CD'
    let tag = 'He'
    let nameOfReactants = ''
    let ratek3 = 'k31'
    let ratekCID = 'kCID1'
    let selectedFile = ''
    let totalMassKey = []
    let k3Guess = '1e-30'
    let kCIDGuess = '1e-15'

    async function browse_folder() {
        const result = await browse({ dir: true })
        if (!result) return

        currentLocation = result
        window.db.set('kinetics_location', currentLocation)
        console.log(result, currentLocation)
    }

    const updateFiles = (node = null) => {
        if (!fs.existsSync(currentLocation))
            return window.createToast('Invalid location', 'danger')
        window.db.set('kinetics_location', currentLocation)
        node?.target.classList.add('rotateIn')
        fileCollections = fs
            .readdirSync(currentLocation)
            .filter((f) => f.endsWith('_scan.json'))
            .map((f) => f.split('.')[0].replace('_scan', '.scan'))
    }

    $: if (currentLocation) {
        updateFiles()
    }

    let currentData = {}
    let currentDataBackup = {}

    const sliceData = (compute = true) => {
        console.log('slicing data')
        if (!selectedFile.endsWith('.scan')) return

        totalMassKey.forEach(({ mass }) => {
            const newData = cloneDeep(currentDataBackup)[mass]
            newData.x = newData.x.slice(timestartIndexScan)
            newData.y = newData.y.slice(timestartIndexScan)
            newData['error_y']['array'] =
                newData['error_y']['array'].slice(timestartIndexScan)
            currentData[mass] = newData
        })

        if (useParamsFile) {
            const masses = totalMassKey
                .filter((m) => m.included)
                .map(({ mass }) => mass.trim())
            const parentCounts =
                currentData?.[masses[0]]?.['y']?.[0]?.toFixed(0)
            if (!defaultInitialValues) return
            initialValues = [
                parentCounts,
                ...Array(masses.length - 1).fill(1),
            ].join(', ')

            return
        }

        if (compute) {
            computeOtherParameters()
        }
    }

    let maxTimeIndex = 5

    function computeParameters() {
        timestartIndexScan = 0

        const currentJSONfile = pathJoin(
            currentLocation,
            selectedFile.replace('.scan', '_scan.json')
        )

        ;[currentData] = fs.readJsonSync(currentJSONfile)
        if (!currentData) return
        currentDataBackup = cloneDeep(currentData)

        const totalMass = Object.keys(currentData).filter((m) => m !== 'SUM')
        totalMassKey = totalMass.map((m) => ({
            mass: m,
            id: getID(),
            included: true,
        }))
        maxTimeIndex = currentData[totalMass[0]].x.length - 5
        sliceData(false)
        computeOtherParameters()
    }

    let useParamsFile = false
    const kinetics_params_file = persistentWritable(
        'kinetics_params_file',
        'kinetics.params.json'
    )

    $: paramsFile = pathJoin(configDir, $kinetics_params_file)

    const updateParamsFile = () => {
        let contents = {}
        if (fs.existsSync(paramsFile)) {
            ;[contents] = fs.readJsonSync(paramsFile)
        }
        contents[selectedFile] = {
            ratek3,
            ratekCID,
            legends,
            totalMassKey,
            initialValues,
            nameOfReactants,
            timestartIndexScan,
            $fit_config_filename,
            kineticEditorFilename,
        }

        fs.outputJsonSync(paramsFile, contents)
        window.createToast(`saved: ${basename(paramsFile)}`, 'success')
        params_found = true
    }

    let params_found = false

    const readFromParamsFile = (event) => {
        params_found = false
        if (!(useParamsFile && fs.existsSync(paramsFile))) return

        const [data] = fs.readJsonSync(paramsFile)
        const contents = data?.[selectedFile]
        console.log('no data available')

        if (!contents) return
        ;({
            initialValues,
            ratek3,
            ratekCID,
            nameOfReactants,
            totalMassKey,
            timestartIndexScan,
            legends,
            kineticEditorFilename,
        } = contents)

        if (contents['$fit_config_filename']) {
            $fit_config_filename = contents['$fit_config_filename']
        }

        console.log('read from file', contents)
        params_found = true
    }

    let legends = ''

    function computeOtherParameters() {
        readFromParamsFile()
        if (params_found) return

        const masses = totalMassKey
            .filter((m) => m.included)
            .map(({ mass }) => mass.trim())
        if (masses.length < 2) return
        const parentCounts = currentData?.[masses[0]]?.['y']?.[0]?.toFixed(0)

        if (defaultInitialValues) {
            initialValues = [
                parentCounts,
                ...Array(masses.length - 1).fill(1),
            ].join(', ')
        }

        nameOfReactants = `${molecule}, ${molecule}${tag}`
        legends = `${molecule}$^+$, ${molecule}$^+$${tag}`
        ;(ratek3 = 'k31'), (ratekCID = 'kCID1')

        for (let index = 2; index < masses.length; index++) {
            ratek3 += `, k3${index}`
            ratekCID += `, kCID${index}`
            nameOfReactants += `, ${molecule}${tag}${index}`
            legends += `, ${molecule}$^+$${tag}$_${index}$`
        }
    }

    let calibrationFactor = 1
    let update_pbefore = true

    $: if (srgMode) {
        calibrationFactor = 1
        if (update_pbefore) {
            pbefore = Number(7e-5).toExponential(0)
        }
    } else {
        calibrationFactor = 200
        if (update_pbefore) {
            pbefore = Number(1e-8).toExponential(0)
        }
    }

    let numberDensity = 0
    const computeNumberDensity = async () => {
        await tick()
        const constantValue = 4.2e17
        const pDiff = Number(pafter) - Number(pbefore)
        calibrationFactor = Number(calibrationFactor)
        temp = Number(temp)
        numberDensity = Number(
            (constantValue * calibrationFactor * pDiff) / temp ** 0.5
        ).toExponential(3)
    }

    $: if (
        pbefore ||
        pafter ||
        temp ||
        calibrationFactor ||
        config_content[selectedFile]
    ) {
        computeNumberDensity()
    }

    $: if (selectedFile.endsWith('.scan')) {
        console.log("updating paramaeters")
        computeParameters()
        kineticEditorFilename =
            basename(selectedFile).split('.')[0] + '-kineticModel.md'
    }

    $: configDir = pathJoin(currentLocation, '../configs')
    let config_file = ''
    let config_filelists = []
    const readConfigDir = async () => {
        if (!fs.existsSync(configDir))
            return window.createToast('Invalid location', 'danger')
        const [files, error] = await fs.readdir(configDir)
        if (error) return window.handleError(error)

        config_filelists = files.filter((file) => file.endsWith('.json'))
    }

    $: if (configDir) {
        readConfigDir()
    }

    let config_content = {}

    function saveCurrentConfig() {
        if (!config_file)
            return window.createToast('Invalid config file', 'danger')

        if (!selectedFile || !fs.existsSync(currentLocation)) {
            return window.createToast('Invalid location or filename', 'danger')
        }
        config_content[selectedFile] = currentConfig
        const [, error] = fs.outputJsonSync(config_file, config_content)
        if (error) {
            return window.handleError(error)
        }

        window.createToast(
            'Config file saved' + basename(config_file),
            'warning'
        )
    }

    function updateConfig() {
        update_pbefore = false
        try {
            if (!config_content[selectedFile]) {
                return window.createToast(
                    'config file not available for selected file: ' +
                        selectedFile,
                    'danger'
                )
            }
            ;({ srgMode, pbefore, pafter, calibrationFactor, temp } =
                config_content[selectedFile])
            srgMode = JSON.parse(srgMode)
        } catch (error) {
            window.createToast(
                'Error while reading the values: Check config file',
                'danger'
            )
        }
    }

    $: if (config_content[selectedFile]) {
        updateConfig()
    }
    let configArray = []

    async function loadConfig() {
        try {
            if (!fs.existsSync(config_file)) {
                console.log(config_file)
                return window.createToast(
                    `Config file not available: ${basename(config_file)}`,
                    'danger'
                )
            }
            ;[config_content] = fs.readJsonSync(config_file)

            configArray = Object.keys(config_content).map((filename) => ({
                filename,
                ...config_content[filename],
                id: getID(),
            }))

            if (window.db.get('active_tab')?.toLowerCase() === 'kinetics') {
                window.createToast(
                    `Config file loaded: ${basename(config_file)}`,
                    'warning'
                )
            }
        } catch (error) {
            window.handleError(error)
        }
    }

    async function kineticSimulation(e) {
        try {
            if (!selectedFile) {
                return window.handleError('Select a file')
            }
            if (!currentData) {
                return window.handleError('No data available')
            }
            if (!fs.existsSync(kineticfile)) {
                return window.handleError('Compute and save kinetic equation')
            }

            const masses = totalMassKey
                .filter((m) => m.included)
                .map(({ mass }) => mass.trim())

            if (masses.length < 2) {
                return window.handleError(
                    'atleast two reactants are required for kinetics'
                )
            }
            const nameOfReactantsArray = nameOfReactants
                .split(',')
                .map((m) => m.trim())

            sliceData(false)

            const data = {}
            masses.forEach((mass, index) => {
                data[nameOfReactantsArray[index]] = currentData[mass]
            })

            let kinetic_plot_adjust_configs_obj = {}
            try {
                kinetic_plot_adjust_configs_obj = $kinetic_plot_adjust_configs
                    .replaceAll('=', ':')
                    .split(',')
                    .map((_v0) =>
                        _v0
                            .trim()
                            .split(':')
                            .map((_v1) => `"${_v1}"`)
                            .join(':')
                    )
                    .join()
                kinetic_plot_adjust_configs_obj = JSON.parse(
                    `{${kinetic_plot_adjust_configs_obj}}`
                )
            } catch (error) {
                kinetic_plot_adjust_configs_obj = {}
                console.error(error)
            }

            const args = {
                tag,
                data,
                temp,
                ratek3,
                k3Guess,
                molecule,
                ratekCID,
                legends,
                kCIDGuess,
                selectedFile,
                numberDensity,
                $fit_config_filename,
                nameOfReactantsArray,
                kineticEditorFilename,
                kinetic_plot_adjust_configs_obj,
                kinetic_file_location: currentLocation,
                initialValues: initialValues.split(','),
            }
            computePy_func({ e, pyfile: 'kineticsCode', args, general: true })
        } catch (error) {
            window.handleError(error)
        }
    }
    let defaultInitialValues = true

    let initialValues = ''
    let adjustConfig = false

    $: currentConfig = { srgMode, pbefore, pafter, calibrationFactor, temp }

    let kineticEditorFilename = ''
    // $: if(selectedFile) {
    //     kineticEditorFilename = basename(selectedFile).split('.')[0] + '-kineticModel.md'
    // }
    $: console.log(kineticEditorFilename)

    $: kineticfile = pathJoin(currentLocation, kineticEditorFilename)
    let reportRead = false
    let reportSaved = false
    const fit_config_filename = persistentWritable(
        'kinetics_fitted_values',
        'kinetics.fit.json'
    )
    onMount(() => {
        loadConfig()
        if (fileCollections.length > 0) {
            selectedFile = fileCollections[0]
        }
    })

    let kinetic_plot_adjust_dialog_active = false
    const kinetic_plot_adjust_configs = persistentWritable(
        'kinetic_plot_adjust_configs',
        'top=0.905,\nbottom=0.135,\nleft=0.075,\nright=0.59,\nhspace=0.2,\nwspace=0.2'
    )

    let auto_compute_params = true
</script>

<KineticConfigTable
    {configArray}
    {currentLocation}
    {loadConfig}
    {readConfigDir}
    {config_filelists}
    bind:config_file
    bind:active={adjustConfig}
/>
<MatplotlibDialog
    bind:open={kinetic_plot_adjust_dialog_active}
    bind:value={$kinetic_plot_adjust_configs}
/>

<LayoutDiv id="Kinetics">
    <svelte:fragment slot="header_content__slot">
        <div class="location__div box">
            <button class="button is-link" on:click={browse_folder}
                >Browse</button
            >
            <Textfield
                bind:value={currentLocation}
                label="Timescan EXPORT data location"
            />
            <i
                class="material-icons animated faster"
                on:animationend={({ target }) =>
                    target?.classList.remove('rotateIn')}
                on:click={updateFiles}
            >
                refresh
            </i>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">
        <div class="main_container__div">
            <div class="align box h-center">
                <CustomSwitch bind:selected={srgMode} label="SRG" />
                <Textfield bind:value={pbefore} label="pbefore" />
                <Textfield bind:value={pafter} label="pafter" />
                <CustomTextSwitch
                    step="0.5"
                    bind:value={calibrationFactor}
                    label="calibrationFactor"
                />
                <CustomTextSwitch
                    step="0.1"
                    bind:value={temp}
                    label="temp(K)"
                />
                <Textfield
                    value={numberDensity}
                    label="numberDensity"
                    disabled
                />
            </div>

            <div class="align box h-center">
                <CustomSelect
                    bind:picked={selectedFile}
                    label="Filename"
                    options={fileCollections}
                />
                <CustomTextSwitch
                    max={maxTimeIndex}
                    bind:value={timestartIndexScan}
                    label="Time Index"
                    on:change={() => sliceData(true)}
                />
                <Textfield bind:value={molecule} label="Molecule" />
                <Textfield bind:value={tag} label="tag" />
            </div>

            <div class="align box h-center" style:flex-direction="column">
                <div class="align h-center">
                    <Textfield
                        bind:value={nameOfReactants}
                        label="nameOfReactants"
                        style="width:30%"
                    />

                    <Textfield
                        bind:value={legends}
                        label="legends"
                        style="width:30%"
                    />
                </div>

                <div class="align h-center">
                    {#each totalMassKey as { mass, id, included } (id)}
                        <span
                            class="tag is-warning"
                            class:is-danger={!included}
                        >
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
                        on:SMUISwitch:change={computeOtherParameters}
                        bind:selected={useParamsFile}
                        label="use params file"
                    />
                    <CustomSelect
                        bind:picked={$kinetics_params_file}
                        label="save-params file (*.params.json)"
                        options={config_filelists.filter((file) =>
                            file.endsWith('.params.json')
                        )}
                        update={readConfigDir}
                    />

                    <button
                        class="button is-link"
                        on:click={computeOtherParameters}>read</button
                    >
                    <button class="button is-link" on:click={updateParamsFile}
                        >update</button
                    >
                    {#if useParamsFile && selectedFile}
                        <span class="tag is-success" class:is-danger={!params_found} transition:fade
                            >{params_found ? `params updated: ${window.basename(selectedFile)}` : 'params not found'}</span
                        >
                    {/if}
                </div>
            </div>

            <div class="align box h-center">
                <CustomSwitch
                    bind:selected={defaultInitialValues}
                    label="defaultInitialValues"
                />
                <Textfield bind:value={initialValues} label="initialValues" />
                <Textfield bind:value={ratek3} label="ratek3" />
                <Textfield bind:value={k3Guess} label="k3Guess" />
                <Textfield bind:value={ratekCID} label="ratekCID" />
                <Textfield bind:value={kCIDGuess} label="kCIDGuess" />

                <CustomSelect
                    bind:picked={$fit_config_filename}
                    label="fit-config file (*.fit.json)"
                    options={config_filelists.filter((file) =>
                        file.endsWith('.fit.json')
                    )}
                    update={readConfigDir}
                />
            </div>

            <KineticEditor
                {ratek3}
                {ratekCID}
                {nameOfReactants}
                bind:location={currentLocation}
                bind:savefilename={kineticEditorFilename}
                bind:reportSaved
                bind:reportRead
            />
        </div>
    </svelte:fragment>

    <svelte:fragment slot="footer_content__slot">
        <!-- <CustomSwitch bind:selected={auto_compute_params} label="auto-compute" /> -->

        <button
            class="button is-link"
            on:click={() => {
                kinetic_plot_adjust_dialog_active = true
            }}>Adjust plot</button
        >
        <button class="button is-link" on:click={computeParameters}
            >Compute parameters</button
        >
        <button class="button is-warning" on:click={loadConfig}
            >loadConfig</button
        >
        <button class="button is-link" on:click={saveCurrentConfig}
            >saveCurrentConfig</button
        >

        <i class="material-icons" on:click={() => (adjustConfig = true)}
            >settings</i
        >
        <button
            class="button is-link"
            id="kinetic-submit-button"
            on:click={kineticSimulation}>Submit</button
        >
    </svelte:fragment>
</LayoutDiv>

<style lang="scss">
    .location__div {
        display: grid;
        grid-auto-flow: column;
        grid-template-columns: auto 1fr auto;
        align-items: baseline;
        gap: 1em;
        padding: 0.5em;
    }

    .main_container__div {
        display: grid;
        grid-row-gap: 1em;
        padding-right: 1em;
    }
    .box {
        margin: 0;
        padding: 0.5em;
        border: solid 1px #fff7;
    }
</style>
