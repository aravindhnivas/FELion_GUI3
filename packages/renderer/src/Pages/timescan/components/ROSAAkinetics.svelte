<script>
    import { onMount, tick } from 'svelte'
    import Textfield from '@smui/textfield'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import LayoutDiv from '$components/LayoutDiv.svelte'
    import { cloneDeep } from 'lodash-es'
    import computePy_func from '$src/Pages/general/computePy'
    import KineticConfigTable from './KineticConfigTable.svelte'
    import KineticEditor from './KineticEditor.svelte'

    import { browse } from '$components/Layout.svelte'

    let currentLocation = db.get('kinetics_location') || ''

    let timestartIndexScan = 0
    let fileCollections = []
    let srgMode = true
    let pbefore = 0
    let pafter = 0
    let temp = 5
    let molecule = 'CD'
    let tag = 'He'
    let massOfReactants = ''
    let nameOfReactants = ''
    let ratek3 = 'k31'
    let ratekCID = 'kCID1'
    let selectedFile = ''
    let totalMass = []
    let k3Guess = '1e-30'
    let kCIDGuess = '1e-15'

    async function browse_folder() {
        const result = await browse({ dir: true })
        if (!result) return

        currentLocation = result
        db.set('kinetics_location', currentLocation)
        console.log(result, currentLocation)
    }

    const updateFiles = (node = null) => {
        if (!fs.existsSync(currentLocation))
            return window.createToast('Invalid location', 'danger')
        db.set('kinetics_location', currentLocation)
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

    const sliceData = () => {
        if (selectedFile.endsWith('.scan')) {
            totalMass.forEach((massKey) => {
                const newData = cloneDeep(currentDataBackup)[massKey]
                newData.x = newData.x.slice(timestartIndexScan)
                newData.y = newData.y.slice(timestartIndexScan)
                newData['error_y']['array'] =
                    newData['error_y']['array'].slice(timestartIndexScan)
                currentData[massKey] = newData
            })

            computeOtherParameters()
        }
    }

    let maxTimeIndex = 5

    function computeParameters() {
        const currentJSONfile = pathJoin(
            currentLocation,
            selectedFile.replace('.scan', '_scan.json')
        )
        console.log(currentJSONfile)

        currentData = fs.readJsonSync(currentJSONfile)
        currentDataBackup = cloneDeep(currentData)

        if (currentData) {
            totalMass = Object.keys(currentData)
            totalMass = totalMass.slice(0, totalMass.length - 1)
            totalMass.forEach((m) => {
                modifiedTotalMass[m] = { included: true }
            })

            maxTimeIndex = currentData[totalMass[0]].x.length - 5

            massOfReactants = totalMass.join(', ')
            sliceData()
            console.log({ maxTimeIndex })
        }
    }

    function computeOtherParameters() {
        masses = massOfReactants.split(',').map((m) => m.trim())

        const requiredLength = masses.length
        if (defaultInitialValues && masses) {
            initialValues = [
                currentData?.[masses[0]]['y'][0]?.toFixed(0),
                ...Array(requiredLength - 1).fill(1),
            ]
        }
        nameOfReactants = `${molecule}, ${molecule}${tag}`
        ;(ratek3 = 'k31'), (ratekCID = 'kCID1')

        for (let index = 2; index < requiredLength; index++) {
            ratek3 += `, k3${index}`
            ratekCID += `, kCID${index}`
            nameOfReactants += `, ${molecule}${tag}${index}`
        }
    }

    let masses
    let calibrationFactor = 1
    let update_pbefore = true

    $: if (massOfReactants) {
        computeOtherParameters()
    }
    $: if (srgMode) {
        calibrationFactor = 1
        if (update_pbefore) pbefore = Number(7e-5).toExponential(0)
    } else {
        calibrationFactor = 200
        if (update_pbefore) pbefore = Number(1e-8).toExponential(0)
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
        computeParameters()
    }

    const config_file_ROSAAkinetics = 'config_file_ROSAAkinetics.json'

    $: config_file = pathJoin(currentLocation, config_file_ROSAAkinetics)
    let config_content = {}

    function saveCurrentConfig() {
        if (!selectedFile || !fs.existsSync(currentLocation)) {
            return window.createToast('Invalid location or filename', 'danger')
        }
        config_content[selectedFile] = currentConfig
        fs.outputJsonSync(config_file, config_content)
        window.createToast(
            'Config file saved' + config_file_ROSAAkinetics,
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
            if (fs.existsSync(config_file)) {
                config_content = fs.readJsonSync(config_file)

                configArray = Object.keys(config_content).map((filename) => ({
                    filename,
                    ...config_content[filename],
                    id: getID(),
                }))

                if (db.get('active_tab')?.toLowerCase() === 'kinetics') {
                    window.createToast(
                        'Config file loaded: ' + config_file_ROSAAkinetics,
                        'warning'
                    )
                }
            } else {
                window.createToast('config file not available', 'danger')
            }
        } catch (error) {
            window.handleError(error)
        }
    }

    async function kineticSimulation(e) {
        try {
            let error = false
            if (!selectedFile) {
                createToast('Select a file', 'danger')
                error = true
            }
            if (!currentData) {
                createToast('No data available', 'danger')
                error = true
            }
            if (!fs.existsSync(kineticfile)) {
                createToast('Compute and save kinetic equation', 'danger')
                error = true
            }

            if (error) {
                const submitbtn = document.getElementById(
                    'kinetic-submit-button'
                )
                const backgroundColor = submitbtn.style.backgroundColor
                submitbtn.style.backgroundColor = '#f14668'
                submitbtn.disabled = true
                setTimeout(() => {
                    submitbtn.style.backgroundColor = backgroundColor
                    submitbtn.disabled = false
                }, 2000)

                return
            }

            const nameOfReactantsArray = nameOfReactants
                .split(',')
                .map((m) => m.trim())
            const data = {}

            massOfReactants
                .split(',')
                .map((mass) => mass.trim())
                .forEach(
                    (mass, i) =>
                        (data[nameOfReactantsArray[i]] = currentData[mass])
                )

            if (typeof initialValues === 'string') {
                initialValues = initialValues.split(',')
            }
            const args = {
                tag,
                data,
                temp,

                ratek3,
                k3Guess,
                molecule,
                ratekCID,
                kCIDGuess,
                selectedFile,
                initialValues,
                numberDensity,
                currentLocation,
                nameOfReactantsArray,
                kineticEditorLocation,
                kineticEditorFilename,
            }
            computePy_func({ e, pyfile: 'kineticsCode', args, general: true })
        } catch (error) {
            window.handleError(error)
        }
    }

    let pyProcesses = []
    let defaultInitialValues = true

    let initialValues = ''
    let adjustConfig = false

    $: currentConfig = { srgMode, pbefore, pafter, calibrationFactor, temp }
    $: kineticEditorFilename =
        basename(selectedFile).split('.')[0] + '-kineticModel.md'

    let kineticEditorFiletype = 'kinetics'
    let kineticEditorLocation =
        db.get(`${kineticEditorFiletype}-report-md`) || currentLocation

    $: kineticfile = pathJoin(kineticEditorLocation, kineticEditorFilename)
    let reportRead = false
    let reportSaved = false
    let modifiedTotalMass = {}
    onMount(() => {
        loadConfig()
        if (fileCollections.length > 0) {
            selectedFile = fileCollections[0]
        }
    })

    const update_included_masses = ({ node, mass }) => {
        modifiedTotalMass[mass].included = !modifiedTotalMass[mass].included
        node?.classList?.toggle('is-danger')
        let newTotalMass = []

        for (const mass in modifiedTotalMass) {
            if (modifiedTotalMass[mass].included) {
                newTotalMass = [...newTotalMass, mass]
            }
        }
        massOfReactants = newTotalMass.join(', ')
    }
</script>

<KineticConfigTable {configArray} {config_file} bind:active={adjustConfig} />

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
                    on:change={sliceData}
                />
                <Textfield bind:value={molecule} label="Molecule" />
                <Textfield bind:value={tag} label="tag" />
            </div>

            <div class="align box h-center">
                <Textfield
                    bind:value={massOfReactants}
                    label="massOfReactants"
                />
                <Textfield
                    bind:value={nameOfReactants}
                    label="nameOfReactants"
                />

                <div class="align h-center">
                    {#each totalMass as mass (mass)}
                        <span class="tag is-warning">
                            {mass}
                            <button
                                class="delete is-small"
                                on:click={({ target }) => {
                                    update_included_masses({
                                        node: target?.parentNode,
                                        mass,
                                    })
                                }}
                            />
                        </span>
                    {/each}
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
            </div>

            <KineticEditor
                {massOfReactants}
                {ratek3}
                {ratekCID}
                {nameOfReactants}
                bind:kineticEditorLocation
                bind:kineticEditorFilename
                bind:reportSaved
                bind:reportRead
            />
        </div>
    </svelte:fragment>

    <svelte:fragment slot="footer_content__slot">
        {#if pyProcesses.length > 0}
            <button
                class="button is-danger"
                on:click={() => {
                    pyProcesses.at(-1).kill()
                    pyProcesses.pop()
                }}>Stop</button
            >
        {/if}

        <button class="button is-link" on:click={computeParameters}
            >Compute parameters</button
        >
        <button class="button is-link" on:click={loadConfig}>loadConfig</button>
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
