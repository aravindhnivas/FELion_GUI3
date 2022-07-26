<script lang="ts">
    import { persistentWritable } from '$src/js/persistentStore'
    import { onMount } from 'svelte'
    // import { boltzmanConstant } from '$src/js/constants'
    import { cloneDeep } from 'lodash-es'
    import Textfield from '@smui/textfield'

    // import CustomSwitch from '$components/CustomSwitch.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'

    import LayoutDiv from '$components/LayoutDiv.svelte'
    import computePy_func from '$src/Pages/general/computePy'
    import KineticConfigTable from './controllers/KineticConfigTable.svelte'

    import KineticEditor from './KineticEditor.svelte'
    import MatplotlibDialog from './MatplotlibDialog.svelte'
    import { browse } from '$components/Layout.svelte'

    import ButtonBadge from '$components/ButtonBadge.svelte'
    import RateConstants from './controllers/RateConstants.svelte'
    import RateInitialise from './controllers/RateInitialise.svelte'
    import KlossChannels from './controllers/channels/KlossChannels.svelte'
    import KineticsNumberDensity from './controllers/KineticsNumberDensity.svelte'
    // import { activePage } from '$src/sveltewritables'
    import type { mainDataType, dataType, totalMassKeyType, loss_channelsType } from '$src/Pages/timescan/types/types'

    import Accordion from '@smui-extra/accordion'
    import CustomPanel from '$components/CustomPanel.svelte'
    //
    let currentLocation = (window.db.get('kinetics_location') as string) || ''
    // $: config_location = window.path.join(currentLocation, '../configs')

    let timestartIndexScan = 0
    let fileCollections: string[] = []
    let molecule = 'CD'
    let tag = 'He'
    let nameOfReactants = ''
    // let ratek3 = 'k31'
    // let ratekCID = 'kCID1'
    let selectedFile = ''
    let totalMassKey: totalMassKeyType = []
    // let k3Guess = '0, 0.5, 1e-3'
    // let kCIDGuess = '0, 2, 1e-3'

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
            if (!newData) return window.createToast(`${mass} not found`, 'danger', { target: 'left' })
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
        console.log('compute parameters')
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
    $: paramsFile = window.path.join(configDir, $kinetics_params_file || '')
    $: paramsData = {
        // ratek3,
        // k3Guess,
        // ratekCID,
        // kCIDGuess,
        legends,
        totalMassKey,
        initialValues,
        molecule,
        tag,
        nameOfReactants,
        timestartIndexScan,
        $fit_config_filename,
        kineticEditorFilename,
        // loss_channels,
        tagFile,
    }
    let load_data_loss_channels
    const params_load = (data) => {
        ;({
            // ratek3,
            // k3Guess,
            // ratekCID,
            // kCIDGuess,
            legends,
            totalMassKey,
            initialValues,
            molecule,
            tag,
            nameOfReactants,
            timestartIndexScan,
            kineticEditorFilename,
            // loss_channels,
        } = data)

        if (!(molecule && tag)) {
            if (nameOfReactants) {
                molecule = nameOfReactants.split(',').at(0)
                tag = nameOfReactants.split(',').at(1).split(molecule).at(-1)
            }
        }
        if (data['$fit_config_filename']) {
            $fit_config_filename = data['$fit_config_filename']
        }

        if (data['tagFile']) {
            tagFile = data['tagFile']
        }
        load_data_loss_channels?.(false)
        params_found = true
    }

    const updateParamsFile = () => {
        let contents = {}
        if (window.fs.existsSync(paramsFile)) {
            ;[contents] = window.fs.readJsonSync(paramsFile)
        }

        contents[selectedFile] ??= { tag: {}, default: {} }
        contents[selectedFile].tag ??= {}
        contents[selectedFile].default ??= {}

        if (useTaggedFile) {
            if (tagFile.length === 0) {
                return window.createToast('Please select/write a tag name', 'danger', { target: 'left' })
            }
            contents[selectedFile].tag[tagFile] = paramsData
        } else {
            contents[selectedFile].default = paramsData
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
    let tagOptions: string[] = []

    const readFromParamsFile = (event?: Event) => {
        params_found = false
        tagOptions = []
        if (!(useParamsFile && window.fs.isFile(paramsFile))) return

        const [data] = window.fs.readJsonSync(paramsFile)
        if (!data) return window.createToast('no data found while reading file', 'danger', { target: 'left' })

        const contents = data[selectedFile]
        if (!contents) return window.createToast('no contents in the data', 'danger', { target: 'left' })

        if (contents.tag) {
            tagOptions = Object.keys(contents.tag)

            tagFile ||= tagOptions[0] || ''
        }
        let setContents = {}
        if (useTaggedFile) {
            if (!contents.tag?.[tagFile]) {
                return window.createToast('no data available for this tag', 'danger', { target: 'left' })
            }
            setContents = contents.tag[tagFile]
        } else {
            setContents = contents.default
        }
        if (!setContents) return window.createToast('no contents available while reading', 'danger', { target: 'left' })
        params_load(setContents)
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
        // ;(ratek3 = 'k31'), (ratekCID = 'kCID1')

        for (let index = 2; index < masses.length; index++) {
            // ratek3 += `, k3${index}`
            // ratekCID += `, kCID${index}`
            nameOfReactants += `, ${molecule}${tag}${index}`
            legends += `, ${molecule}$^+$${tag}$_${index}$`
        }
    }

    // let numberDensity = 0

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

            // let modified_rate_constants = [ratek3, ratekCID]
            // loss_channels.forEach(({ type, name }) => {
            //     if (type === 'forwards') return (modified_rate_constants[0] += `, ${name}`)
            //     modified_rate_constants[1] += `, ${name}`
            // })
            const args = {
                tag,
                data,
                molecule,
                legends,
                // ratek3: modified_rate_constants[0],
                // k3Guess,
                // ratekCID: modified_rate_constants[1],
                // kCIDGuess,
                selectedFile,
                numberDensity: nHe,
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
    // let adjustConfig = false
    let kineticEditorFilename = ''
    $: kineticfile = window.path.join(currentLocation, kineticEditorFilename)

    let reportRead = false
    let reportSaved = false
    const fit_config_filename = persistentWritable('kinetics_fitted_values', 'kinetics.fit.json')
    let loss_channels: loss_channelsType[] = []
    let rateConstantMode = false

    onMount(() => {
        // loadConfig()
        selectedFile = fileCollections[0] || ''
    })

    let kinetic_plot_adjust_dialog_active = false
    let show_numberDensity = false
    let show_fileConfigs = false
    let nHe = ''
    const kinetic_plot_adjust_configs = persistentWritable(
        'kinetic_plot_adjust_configs',
        'top=0.905,\nbottom=0.135,\nleft=0.075,\nright=0.59,\nhspace=0.2,\nwspace=0.2'
    )
</script>

<MatplotlibDialog bind:open={kinetic_plot_adjust_dialog_active} bind:value={$kinetic_plot_adjust_configs} />
<KineticsNumberDensity bind:active={show_numberDensity} bind:nHe {selectedFile} {fileCollections} {configDir} />
<KineticConfigTable bind:active={show_fileConfigs} {configDir} />

<LayoutDiv id="ROSAA-kinetics">
    <svelte:fragment slot="header_content__slot">
        <div class="location__div box">
            <button class="button is-link" on:click={browse_folder}>Browse</button>
            <Textfield bind:value={currentLocation} label="Timescan EXPORT data location" />
            <i
                class="material-symbols-outlined animate__animated animate__faster"
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
            <Accordion multiple style="width: 100%;">
                <CustomPanel loaded={nHe?.length > 0} label="Number density">
                    <Textfield value={nHe || ''} label="numberDensity" disabled />
                    <button
                        class="button is-link"
                        on:click={() => {
                            show_numberDensity = true
                        }}>Open number density modal</button
                    >
                    <button
                        class="button is-link"
                        on:click={() => {
                            show_fileConfigs = true
                        }}>Show file configs</button
                    >
                </CustomPanel>

                <RateInitialise
                    loaded={params_found}
                    {totalMassKey}
                    bind:useParamsFile
                    bind:nameOfReactants
                    bind:legends
                    {computeOtherParameters}
                >
                    <svelte:fragment slot="basic-infos">
                        <div class="align v-center">
                            <CustomTextSwitch
                                max={maxTimeIndex}
                                bind:value={timestartIndexScan}
                                label="Time Index"
                                on:change={() => {
                                    sliceData(true)
                                }}
                            />
                            <Textfield bind:value={molecule} label="Molecule" />
                            <Textfield bind:value={tag} label="tag" />
                            <div class="parm_save__div">
                                <button class="button is-warning" on:click={() => computeOtherParameters()}>load</button
                                >
                                <TextAndSelectOptsToggler
                                    bind:value={$kinetics_params_file}
                                    label="fit-config file (*.params.json)"
                                    lookFor=".params.json"
                                    lookIn={configDir}
                                />
                                <button class="button is-link" on:click={updateParamsFile}>save</button>
                            </div>
                        </div>
                    </svelte:fragment>
                    <svelte:fragment slot="rate-constants">
                        <RateConstants
                            {configDir}
                            bind:defaultInitialValues
                            bind:initialValues
                            bind:kinetics_fitfile={$fit_config_filename}
                        />
                    </svelte:fragment>
                </RateInitialise>

                <KlossChannels
                    bind:load_data={load_data_loss_channels}
                    bind:loss_channels
                    {nameOfReactants}
                    bind:rateConstantMode
                    {...{
                        selectedFile,
                        useTaggedFile,
                        tagFile,
                        configDir,
                        useParamsFile,
                    }}
                />
            </Accordion>
            <KineticEditor
                {...{
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
        <CustomCheckbox on:change={computeParameters} bind:value={useParamsFile} label="useParams" />
        <CustomCheckbox bind:value={useTaggedFile} label="useTag" />
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
        <i class="material-symbols-outlined" on:click={() => (kinetic_plot_adjust_dialog_active = true)}>settings</i>
        <ButtonBadge id="kinetic-submit-button" on:click={kineticSimulation} />
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

    .parm_save__div {
        align-items: flex-end;
        justify-content: flex-end;
        display: flex;
        gap: 1em;
        margin-left: auto;
    }
</style>
