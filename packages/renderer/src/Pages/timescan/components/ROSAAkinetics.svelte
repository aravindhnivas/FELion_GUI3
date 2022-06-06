<script lang="ts">
    import { persistentWritable } from '$src/js/persistentStore'
    import { onMount, tick } from 'svelte'
    import { boltzmanConstant } from '$src/js/constants'
    import { cloneDeep } from 'lodash-es'
    import Textfield from '@smui/textfield'

    import CustomSwitch from '$components/CustomSwitch.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'

    import LayoutDiv from '$components/LayoutDiv.svelte'
    import computePy_func from '$src/Pages/general/computePy'
    import KineticConfigTable from './KineticConfigTable.svelte'

    import KineticEditor from './KineticEditor.svelte'
    import MatplotlibDialog from './MatplotlibDialog.svelte'
    import { browse } from '$components/Layout.svelte'

    // import { fade } from 'svelte/transition'
    import RateConstants from './controllers/RateConstants.svelte'
    import RateInitialise from './controllers/RateInitialise.svelte'
    import KlossChannels from './controllers/channels/KlossChannels.svelte'
    import KineticsNumberDensity from './controllers/KineticsNumberDensity.svelte'
    import { activePage } from '$src/sveltewritables'
    import type { mainDataType, dataType, totalMassKeyType, loss_channelsType } from '$src/Pages/timescan/types/types'

    let currentLocation = (window.db.get('kinetics_location') as string) || ''
    $: config_location = window.path.join(currentLocation, '../configs')

    let timestartIndexScan = 0
    let fileCollections: string[] = []
    let molecule = 'CD'
    let tag = 'He'
    let nameOfReactants = ''
    let ratek3 = 'k31'
    let ratekCID = 'kCID1'
    let selectedFile = ''
    let totalMassKey: totalMassKeyType = []
    let k3Guess = '0, 0.5, 1e-3'
    let kCIDGuess = '0, 2, 1e-3'

    async function browse_folder() {
        const [result] = await browse()
        if (!result) return
        currentLocation = result
        window.db.set('kinetics_location', currentLocation)
        console.log(result, currentLocation)
    }

    const updateFiles = (node?: ButtonClickEvent) => {
        if (!window.fs.existsSync(currentLocation)) {
            return window.createToast('Invalid location', 'danger', { target: 'left' })
        }
        window.db.set('kinetics_location', currentLocation)

        node?.target.classList.add('animate__rotateIn')

        fileCollections = window.fs
            .readdirSync(currentLocation)
            .filter((f) => f.endsWith('_scan.json'))
            .map((f) => f.split('.')[0].replace('_scan', '.scan'))
        console.log(fileCollections)
    }

    $: if (currentLocation) {
        updateFiles()
    }

    let currentData: mainDataType
    let currentDataBackup: mainDataType

    const sliceSUM = () => {
        const newData: dataType = cloneDeep(currentDataBackup).SUM
        currentData.SUM.x = newData.x.slice(timestartIndexScan)
        currentData.SUM.y = newData.y.slice(timestartIndexScan)
        currentData['SUM']['error_y']['array'] = newData['error_y']['array'].slice(timestartIndexScan)
    }

    const sliceData = (compute = true) => {
        console.log('slicing data')
        if (!selectedFile.endsWith('.scan')) return

        totalMassKey.forEach(({ mass }) => {
            const newData: dataType = cloneDeep(currentDataBackup)[mass]
            newData.x = newData.x.slice(timestartIndexScan)
            newData.y = newData.y.slice(timestartIndexScan)
            newData['error_y']['array'] = newData['error_y']['array'].slice(timestartIndexScan)
            currentData[mass] = newData
        })

        sliceSUM()

        if (useParamsFile) {
            const masses = totalMassKey.filter((m) => m.included).map(({ mass }) => mass.trim())
            const parentCounts = currentData?.[masses[0]]?.['y']?.[0]?.toFixed(0)
            if (!defaultInitialValues) return
            initialValues = [parentCounts, ...Array(masses.length - 1).fill(1)].join(', ')

            return
        }

        if (compute) {
            computeOtherParameters()
        }
    }

    let maxTimeIndex = 5

    function computeParameters() {
        // includeTrapLoss = false
        tagFile = ''

        timestartIndexScan = 0
        loss_channels = []

        const currentJSONfile = window.path.join(currentLocation, selectedFile.replace('.scan', '_scan.json'))

        ;[currentData] = window.fs.readJsonSync(currentJSONfile)
        if (!currentData) return
        currentDataBackup = cloneDeep(currentData)
        console.log({ currentData })
        const totalMass = Object.keys(currentData).filter((m) => m !== 'SUM')
        totalMassKey = totalMass.map((m) => ({
            mass: m,
            id: window.getID(),
            included: true,
        }))
        maxTimeIndex = currentData[totalMass[0]].x.length - 5
        sliceData(false)
        computeOtherParameters()
    }

    let useParamsFile = false
    const kinetics_params_file = persistentWritable('kinetics_params_file', 'kinetics.params.json')

    $: paramsFile = window.path.join(configDir, $kinetics_params_file)

    const params_updatefile_or_getfromfile = ({ updatefile = true, contents }) => {
        if (updatefile) {
            return {
                ratek3,
                k3Guess,
                ratekCID,
                kCIDGuess,
                legends,
                totalMassKey,
                initialValues,
                nameOfReactants,
                timestartIndexScan,
                $fit_config_filename,
                kineticEditorFilename,
                loss_channels,
                // includeTrapLoss,
                tagFile,
            }
        }
        ;({
            ratek3,
            k3Guess,
            ratekCID,
            kCIDGuess,
            legends,
            totalMassKey,
            initialValues,
            nameOfReactants,
            timestartIndexScan,
            kineticEditorFilename,
            loss_channels,
        } = contents)
        if (contents['$fit_config_filename']) {
            $fit_config_filename = contents['$fit_config_filename']
        }

        // if (contents['includeTrapLoss']) {
        //     includeTrapLoss = contents['includeTrapLoss']
        // }

        if (contents['tagFile']) {
            tagFile = contents['tagFile']
        }

        console.log(tagFile)
        params_found = true
    }

    const updateParamsFile = () => {
        let contents = {}
        if (window.fs.existsSync(paramsFile)) {
            ;[contents] = window.fs.readJsonSync(paramsFile)
        }
        const contents_infos = params_updatefile_or_getfromfile({
            updatefile: true,
            contents,
        })

        if (contents[selectedFile] && Object.keys(contents[selectedFile]).length > 0) {
            if (useTaggedFile && tagFile.length > 0) {
                if (contents[selectedFile]?.tag) {
                    contents[selectedFile].tag[tagFile] = contents_infos
                } else {
                    contents[selectedFile].tag = {}
                    contents[selectedFile].tag[tagFile] = contents_infos
                }
            } else {
                if (!contents[selectedFile]?.tag) {
                    contents[selectedFile]['tag'] = {}
                }

                contents[selectedFile] = {
                    ...contents[selectedFile],
                    ...contents_infos,
                }
            }
        } else {
            contents[selectedFile] = { tag: {} }

            if (useTaggedFile && tagFile.length > 0) {
                contents[selectedFile].tag[tagFile] = contents_infos
            } else {
                contents[selectedFile] = {
                    ...contents[selectedFile],
                    ...contents_infos,
                }
            }
        }
        window.fs.outputJsonSync(paramsFile, contents)
        tagOptions = Object.keys(contents[selectedFile].tag)
        window.createToast(`saved: ${window.path.basename(paramsFile)}`, 'success', {
            target: 'left',
        })

        params_found = true
    }

    let params_found = false
    let useTaggedFile = false
    let tagFile = ''
    let tagOptions = []

    const readFromParamsFile = (event?: Event) => {
        params_found = false
        tagOptions = []
        if (!(useParamsFile && window.fs.existsSync(paramsFile))) return
        const [data] = window.fs.readJsonSync(paramsFile)
        const contents = data?.[selectedFile]
        console.log('no data available')

        if (!contents) return
        if (contents?.tag) {
            tagOptions = Object.keys(contents.tag)
            if (tagOptions.length > 0 && !tagFile) {
                tagFile = tagOptions[0]
            }
        }

        let setContents = {}
        if (useTaggedFile) {
            if (!contents?.tag?.[tagFile]) {
                params_found = false
                return
            }
            setContents = contents.tag[tagFile]
        } else {
            setContents = contents
        }
        params_updatefile_or_getfromfile({
            updatefile: false,
            contents: setContents,
        })
        // window.createToast('config loaded', 'success', { target: 'left' })
    }

    let legends = ''

    function computeOtherParameters(forTagged = false) {
        readFromParamsFile()
        if (params_found) return

        const masses = totalMassKey.filter((m) => m.included).map(({ mass }) => mass.trim())
        if (masses.length < 2) return

        const parentCounts = currentData?.[masses[0]]?.['y']?.[0]?.toFixed(0)
        if (forTagged) return
        if (defaultInitialValues) {
            initialValues = [parentCounts, ...Array(masses.length - 1).fill(1)].join(', ')
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

    let numberDensity = 0

    const update_kinetic_filename = (appendName: string) => {
        kineticEditorFilename = window.path.basename(selectedFile).split('.')[0] + appendName
    }
    $: if (selectedFile.endsWith('.scan')) {
        computeParameters()
        update_kinetic_filename('-kineticModel.md')
    }
    $: if (tagFile) {
        update_kinetic_filename(`-${tagFile}-kineticModel.md`)
    }

    $: configDir = window.path.join(currentLocation, '../configs')

    let config_file = ''
    let config_filelists = []

    const readConfigDir = async () => {
        console.log('reading config dir')
        if (!window.fs.existsSync(configDir)) {
            if ($activePage === 'Kinetics') {
                return window.createToast('Invalid location', 'danger', {
                    target: 'left',
                })
            }
            return
        }

        const [files, error] = await window.fs.readdir(configDir)
        if (error) return window.handleError(error)
        config_filelists = files.filter((file) => file.endsWith('.json'))
    }

    $: if (configDir) {
        readConfigDir()
    }
    let config_content = {}

    let configArray = []

    async function loadConfig() {
        try {
            if (!window.fs.existsSync(config_file)) {
                console.log(config_file)
                if ($activePage === 'Kinetics') {
                    return window.createToast(
                        `Config file not available: ${window.path.basename(config_file)}`,
                        'danger',
                        { target: 'left' }
                    )
                }
                return
            }
            ;[config_content] = window.fs.readJsonSync(config_file)

            configArray = Object.keys(config_content).map((filename) => ({
                filename,
                ...config_content[filename],
                id: window.getID(),
            }))

            if ($activePage?.toLowerCase() === 'kinetics') {
                window.createToast(`Config file loaded: ${window.path.basename(config_file)}`, 'warning', {
                    target: 'left',
                })
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
            if (!window.fs.existsSync(kineticfile)) {
                return window.handleError('Compute and save kinetic equation')
            }

            const masses = totalMassKey.filter((m) => m.included).map(({ mass }) => mass.trim())

            if (masses.length < 2) {
                return window.handleError('atleast two reactants are required for kinetics')
            }
            const nameOfReactantsArray = nameOfReactants.split(',').map((m) => m.trim())

            sliceData(false)

            const data = {}
            masses.forEach((mass, index) => {
                data[nameOfReactantsArray[index]] = currentData[mass]
            })
            data['SUM'] = currentData['SUM']
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
                kinetic_plot_adjust_configs_obj = JSON.parse(`{${kinetic_plot_adjust_configs_obj}}`)

                console.log(kinetic_plot_adjust_configs_obj)
            } catch (error) {
                kinetic_plot_adjust_configs_obj = {}
            }

            let modified_rate_constants = [ratek3, ratekCID]
            loss_channels.forEach(({ type, name }) => {
                if (type === 'forwards') return (modified_rate_constants[0] += `, ${name}`)
                modified_rate_constants[1] += `, ${name}`
            })
            const args = {
                tag,
                data,
                ratek3: modified_rate_constants[0],
                k3Guess,
                molecule,
                ratekCID: modified_rate_constants[1],
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
                useTaggedFile,
                tagFile,
            }
            computePy_func({ e, pyfile: 'kineticsCode', args, general: true })
        } catch (error) {
            window.handleError(error)
        }
    }

    let defaultInitialValues = true
    let initialValues = ''
    let adjustConfig = false
    let kineticEditorFilename = ''
    $: kineticfile = window.path.join(currentLocation, kineticEditorFilename)

    let reportRead = false
    let reportSaved = false
    const fit_config_filename = persistentWritable('kinetics_fitted_values', 'kinetics.fit.json')
    let loss_channels: loss_channelsType[] = []
    let rateConstantMode = false

    onMount(() => {
        loadConfig()
        selectedFile = fileCollections[0] || ''
    })

    let kinetic_plot_adjust_dialog_active = false
    let show_numberDensity = false
    let nHe = ''
    const kinetic_plot_adjust_configs = persistentWritable(
        'kinetic_plot_adjust_configs',
        'top=0.905,\nbottom=0.135,\nleft=0.075,\nright=0.59,\nhspace=0.2,\nwspace=0.2'
    )
</script>

<KineticConfigTable
    {configArray}
    {config_location}
    {loadConfig}
    {readConfigDir}
    {config_filelists}
    bind:config_file
    bind:active={adjustConfig}
/>

<MatplotlibDialog bind:open={kinetic_plot_adjust_dialog_active} bind:value={$kinetic_plot_adjust_configs} />

<KineticsNumberDensity
    bind:nHe
    bind:active={show_numberDensity}
    {selectedFile}
    {config_location}
    {fileCollections}
    {config_filelists}
    {readConfigDir}
/>

<LayoutDiv id="ROSAA-kinetics">
    <svelte:fragment slot="header_content__slot">
        <div class="location__div box">
            <button class="button is-link" on:click={browse_folder}>Browse</button>
            <Textfield bind:value={currentLocation} label="Timescan EXPORT data location" />
            <i
                class="material-icons animate__animated animate__faster"
                on:animationend={({ target }) => {
                    target.classList.remove('animate__rotateIn')
                }}
                on:click={updateFiles}
            >
                refresh
            </i>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">
        <div class="main_container__div">
            <div class="align box h-center">
                <Textfield value={nHe || ''} label="numberDensity" disabled />
                <button
                    class="button is-link"
                    on:click={() => {
                        show_numberDensity = true
                    }}>Open number density modal</button
                >
            </div>

            <div class="align box h-center">
                <CustomTextSwitch
                    max={maxTimeIndex}
                    bind:value={timestartIndexScan}
                    label="Time Index"
                    on:change={() => sliceData(true)}
                />
                <Textfield bind:value={molecule} label="Molecule" />
                <Textfield bind:value={tag} label="tag" />
            </div>

            <RateInitialise
                {config_filelists}
                {updateParamsFile}
                {readConfigDir}
                {computeOtherParameters}
                {selectedFile}
                {params_found}
                {totalMassKey}
                {tagOptions}
                bind:tagFile
                bind:useParamsFile
                bind:useTaggedFile
                bind:kinetics_params_file={$kinetics_params_file}
                bind:nameOfReactants
                bind:legends
            />

            <RateConstants
                {readConfigDir}
                {config_filelists}
                bind:defaultInitialValues
                bind:initialValues
                bind:kinetics_fitfile={$fit_config_filename}
                bind:ratek3
                bind:k3Guess
                bind:ratekCID
                bind:kCIDGuess
            />

            <KlossChannels
                bind:loss_channels
                {nameOfReactants}
                bind:rateConstantMode
                {...{
                    selectedFile,
                    useTaggedFile,
                    tagFile,
                    configDir,
                }}
            />

            <KineticEditor
                {...{
                    ratek3,
                    k3Guess,
                    ratekCID,
                    kCIDGuess,
                    nameOfReactants,
                    loss_channels,
                    selectedFile,
                    rateConstantMode,
                }}
                bind:location={currentLocation}
                bind:savefilename={kineticEditorFilename}
                bind:reportSaved
                bind:reportRead
            />
        </div>
    </svelte:fragment>

    <svelte:fragment slot="left_footer_content__slot">
        <CustomCheckbox on:change={() => computeOtherParameters()} bind:value={useParamsFile} label="load" />
        <CustomCheckbox bind:value={useTaggedFile} />
        <TextAndSelectOptsToggler
            bind:value={tagFile}
            options={tagOptions}
            label="tag files"
            update={() => computeOtherParameters()}
            on:change={computeOtherParameters}
        />
    </svelte:fragment>

    <svelte:fragment slot="footer_content__slot">
        <CustomSelect bind:value={selectedFile} label="Filename" options={fileCollections} />
        <button class="button is-link" on:click={computeParameters}>compute</button>
        <i class="material-icons" on:click={() => (kinetic_plot_adjust_dialog_active = true)}>settings</i>
        <button class="button is-link" id="kinetic-submit-button" on:click={kineticSimulation}>Submit</button>
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
