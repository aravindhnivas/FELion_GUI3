<script>
    // import {fade}                   from "svelte/transition";
    import Textfield from '@smui/textfield'
    import { parse as Yml } from 'yaml'
    // import {find}                   from "lodash-es";
    import { browse } from '$components/Layout.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import LayoutDiv from '$components/LayoutDiv.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    // import PyButton                 from "$components/PyButton.svelte"
    import BoltzmanDistribution from './windows/BoltzmanDistribution.svelte'

    import EinsteinCoefficients from './components/EinsteinCoefficients.svelte'
    import CollisionalCoefficients from './components/CollisionalCoefficients.svelte'
    import AttachmentCoefficients from './components/AttachmentCoefficients.svelte'
    import BoxComponent from './components/BoxComponent.svelte'

    import {
        amuToKG,
        DebyeToCm,
        SpeedOfLight,
        PlanksConstant,
        boltzmanConstant,
        VaccumPermitivity,
    } from './functions/constants'
    // import {findAndGetValue}        from "./functions/misc";
    import computePy_func from '$src/Pages/general/computePy'

    //////////////////////////////////////////////////////////////////////////////////////////////////////////

    // export let active = false;

    //////////////////////////////////////////////////////////////////////////////////////////////////////////

    let electronSpin = false
    let zeemanSplit = false

    let [
        mainParameters,
        simulationParameters,
        dopplerLineshape,
        powerBroadening,
    ] = Array(4).fill([])

    let k3 = { constant: [], rate: [] }
    let kCID = { constant: [], rate: [] }
    let attachmentCoefficients = []

    let collisionalRateType = 'excitation'
    $: deexcitation = collisionalRateType === 'deexcitation'

    let showreport = false

    let pyProcesses = []
    let statusReport = ''

    let collisionalRates = []
    let collisionalRateConstants = []
    let einsteinB_rateComputed = false

    const simulation = (e) => {
        if (!fs.existsSync(currentLocation))
            return window.createToast("Location doesn't exist", 'danger')
        if (!configLoaded)
            return window.createToast('Config file not loaded', 'danger')
        if (!transitionFrequency)
            return window.createToast(
                'Transition frequency is not defined',
                'danger'
            )
        if (!einsteinB_rateComputed)
            return window.createToast(
                'Compute einsteinB rate constants',
                'danger'
            )

        if (includeCollision) {
            collisionalRateConstants = [
                ...collisionalCoefficient,
                ...collisionalCoefficient_balance,
            ]
            if (collisionalRateConstants.length < 1)
                return window.createToast(
                    'Compute collisional rate constants',
                    'danger'
                )
        }

        if (includeAttachmentRate) {
            if (k3.constant.length < 1)
                return window.createToast(
                    'Compute attachment rate constants',
                    'danger'
                )
        }

        const collisional_rates = {}
        collisionalRateConstants.forEach(
            (f) => (collisional_rates[f.label] = f.value)
        )

        const main_parameters = {}
        mainParameters.forEach((f) => (main_parameters[f.label] = f.value))

        const simulation_parameters = {}
        simulationParameters.forEach(
            (f) => (simulation_parameters[f.label] = f.value)
        )

        const lineshape_conditions = {}
        dopplerLineshape.forEach(
            (f) => (lineshape_conditions[f.label] = f.value)
        )

        const power_broadening = {}
        powerBroadening.forEach((f) => (power_broadening[f.label] = f.value))

        const einstein_coefficient = { A: {}, B: {}, B_rateConstant: {} }
        einsteinCoefficientA.forEach(
            (f) => (einstein_coefficient.A[f.label] = f.value)
        )
        einsteinCoefficientB.forEach(
            (f) => (einstein_coefficient.B[f.label] = f.value)
        )
        einsteinCoefficientB_rateConstant.forEach(
            (f) => (einstein_coefficient.B_rateConstant[f.label] = f.value)
        )

        const attachment_rate_coefficients = {
            rateConstants: {
                k3: k3.constant.map((rate) => rate.value),
                kCID: kCID.constant.map((rate) => rate.value),
            },
        }

        attachmentCoefficients.forEach(
            (f) => (attachment_rate_coefficients[f.label] = f.value)
        )
        const energy_levels = {}
        energyLevels.forEach((f) => (energy_levels[f.label] = f.value))
        const args = {
            trapTemp,
            variable,
            variableRange,
            numberOfLevels,
            includeCollision,
            includeAttachmentRate,
            gaussian,
            lorrentz,
            includeSpontaneousEmission,
            writefile,
            writeall,
            appendFiles,
            savefilename,
            currentLocation,
            deexcitation,
            collisional_rates,
            main_parameters,
            simulation_parameters,
            einstein_coefficient,
            energy_levels,
            energyUnit,
            power_broadening,
            lineshape_conditions,
            attachment_rate_coefficients,
            electronSpin,
            zeemanSplit,
            excitedFrom,
            excitedTo,
            numberDensity,
            collisionalTemp,
            simulationMethod,
            figure,
        }
        computePy_func({ e, pyfile: 'ROSAA', args, general: true })
    }
    let currentLocation = fs.existsSync(db.get('ROSAA_config_location'))
        ? db.get('ROSAA_config_location')
        : ''

    // let savefilename = ""
    let moleculeName = '',
        tagName = 'He'
    $: savefilename = `${moleculeName}_${tagName}_${
        variable.split('(')[0]
    }_${excitedFrom} - ${excitedTo}`.replaceAll('$', '')
    $: if (fs.existsSync(currentLocation)) {
        db.set('ROSAA_config_location', currentLocation)
    }

    async function browse_folder() {
        const result = await browse({ filetype: 'yml', dir: false })
        if (!result) return
        configFilename = basename(result[0])
        currentLocation = dirname(result[0])
        db.set('ROSAA_config_location', currentLocation)
        db.set('ROSAA_config_file', configFilename)
        // loadConfig()
    }

    const resetConfig = () => {
        // collisionalCoefficient = collisionalCoefficient_balance = collisionalRates = []
        einsteinCoefficientA = einsteinCoefficientB = []
        energyLevels = []
        simulationParameters =
            mainParameters =
            dopplerLineshape =
            powerBroadening =
                []
        attachmentCoefficients = []
        window.createToast('Config file cleared', 'warning')
    }

    let writefile = true
    let includeCollision = true

    let includeAttachmentRate = true
    let includeSpontaneousEmission = true

    let variable = 'time'
    let variableRange = '1e12, 1e16, 10'
    let writeall = true,
        appendFiles = false

    $: if (variable) {
        if (variable === 'time') variableRange = '1e12, 1e16, 10'
        if (variable === 'He density(cm3)') variableRange = '1e12, 5e16, 10'
        if (variable === 'Power(W)') variableRange = '1e-7, 1e-4, 10'
    }
    const variablesList = ['time', 'He density(cm3)', 'Power(W)']

    let einsteinCoefficientA = []
    let einsteinCoefficientB = []
    let einsteinCoefficientB_rateConstant = []

    let collisionalCoefficient = []

    let energyUnit = 'cm-1'
    let numberOfLevels = 3
    let numberDensity = '2e14'
    let energyFilename
    let einsteinFilename
    let collisionalFilename

    $: configFile = window.pathJoin(currentLocation, configFilename)
    $: boltzmanArgs = {
        energyLevels,
        trapTemp,
        electronSpin,
        zeemanSplit,
        energyUnit,
    }

    let configLoaded = false
    let collisionalCoefficient_balance = []
    let configFilename = db.get('ROSAA_config_file') || ''
    async function loadConfig() {
        try {
            // if(fs.existsSync(configFile)) {
            //     if(!fs.existsSync(currentLocation)) {currentLocation = dirname(configFile)};
            //     return setConfig()
            // }
            // configFile = window.pathJoin(currentLocation, configFilename)
            console.log({ configFile })
            if (fs.existsSync(configFile)) {
                return setConfig()
            }
            browse_folder()
            // setConfig()
        } catch (error) {
            window.handleError(error)
        }
    }

    const getYMLFileContents = (filename) => {
        if (fs.existsSync(filename)) {
            const fileContent = fs.readFileSync(filename)
            const YMLcontent = Yml(fileContent)
            return Promise.resolve(YMLcontent)
        } else return Promise.reject(filename + " file doesn't exist")
    }

    const setID = (obj) => ({ ...obj, id: getID() })
    const correctObjValue = (obj) => ({
        ...obj,
        value: obj.value.toExponential(3),
    })

    let trapArea
    let excitedTo = ''
    let excitedFrom = ''
    let upperLevelEnergy
    let lowerLevelEnergy
    let transitionFrequency = 0

    // Doppler linewidth parameters
    let ionMass = 14
    let RGmass = 4
    let ionTemp = 12
    let trapTemp = 5
    let gaussian = 0
    let collisionalTemp = 0
    let Cg = 0 // doppler-broadening proportionality constant

    // Lorrentz linewidth parameters
    let power = '2e-5'
    let dipole = 1
    let lorrentz = 0
    let Cp = 0 // power-broadening proportionality constant

    $: console.log(mainParameters)
    const updateEnergyLevels = () => {
        console.log('energyLevels updated')
        if (!energyLevels)
            return console.warn('No energyLevels defined', energyLevels)
        console.log(energyLevels)
        lowerLevelEnergy =
            energyLevels?.filter((energy) => energy.label == excitedFrom)?.[0]
                ?.value || 0
        upperLevelEnergy =
            energyLevels?.filter((energy) => energy.label == excitedTo)?.[0]
                ?.value || 0

        transitionFrequency = upperLevelEnergy - lowerLevelEnergy
        if (energyUnit == 'cm-1') {
            transitionFrequency *= SpeedOfLight * 1e2 * 1e-6
        }
        updateDoppler()
    }

    const updateDoppler = () => {
        console.log('Changing doppler parameters')
        ;[ionMass, RGmass, ionTemp, trapTemp] = dopplerLineshape.map(
            (f) => f.value
        )

        collisionalTemp = Number(
            (RGmass * ionTemp + ionMass * trapTemp) / (ionMass + RGmass)
        ).toFixed(1)
        const sqrtTerm =
            (8 * boltzmanConstant * Math.log(2) * ionTemp) /
            (ionMass * amuToKG * SpeedOfLight ** 2)
        Cg = Math.sqrt(sqrtTerm)
        gaussian = Number(transitionFrequency * Cg).toFixed(3) // in MHz
    }
    const updatePower = () => {
        ;[dipole, power] = powerBroadening.map((f) => f.value)
        trapArea =
            mainParameters?.filter(
                (params) => params.label === 'trap_area (sq-meter)'
            )?.[0]?.value || ''
        Cp =
            ((2 * dipole * DebyeToCm) / PlanksConstant) *
            Math.sqrt(1 / (trapArea * SpeedOfLight * VaccumPermitivity))
        lorrentz = Number(Cp * Math.sqrt(power) * 1e-6).toFixed(3)
    }

    $: {
        if (energyLevels.length > 1) {
            updateEnergyLevels()
        }
        if (dopplerLineshape.length) {
            updateDoppler()
        }
        if (powerBroadening.length) {
            updatePower()
        }
    }
    const energyInfos = { 'cm-1': [], MHz: [] }
    async function setConfig() {
        try {
            const configFileLocation = dirname(configFile)
            const CONFIG = Yml(fs.readFileSync(configFile))
            console.table(CONFIG)

            let attachmentRateConstants = {}

            ;({
                mainParameters,
                powerBroadening,
                dopplerLineshape,
                simulationParameters,
                attachmentCoefficients,
                attachmentRateConstants,
            } = CONFIG)

            mainParameters = mainParameters.map(setID)
            powerBroadening = powerBroadening.map(setID)
            dopplerLineshape = dopplerLineshape.map(setID)
            simulationParameters = simulationParameters.map(setID)

            attachmentCoefficients = attachmentCoefficients.map(setID)
            k3.constant = attachmentRateConstants.k3
                .map(setID)
                .map(correctObjValue)
            kCID.constant = attachmentRateConstants.kCID
                .map(setID)
                .map(correctObjValue)
            ;({ trapTemp, zeemanSplit, electronSpin, numberDensity } = CONFIG)
            // ({savefilename}         = CONFIG.saveFile);
            moleculeName =
                mainParameters.filter(
                    (params) => params.label == 'molecule'
                )?.[0]?.value || ''
            tagName =
                mainParameters?.filter(
                    (params) => params.label == 'tagging partner'
                )?.[0]?.value || ''
            const { savelocation } = CONFIG.saveFile
            if (fs.existsSync(savelocation)) {
                currentLocation = savelocation
            }

            ;({
                energy: energyFilename,
                einsteinA: einsteinFilename,
                collision: collisionalFilename,
            } = CONFIG.filenames)
            energyFilename = energyFilename
                ? window.pathJoin(configFileLocation, 'files', energyFilename)
                : ''
            einsteinFilename = einsteinFilename
                ? window.pathJoin(configFileLocation, 'files', einsteinFilename)
                : ''
            collisionalFilename = collisionalFilename
                ? window.pathJoin(
                      configFileLocation,
                      'files',
                      collisionalFilename
                  )
                : ''

            let energyLevelsStore = []

            if (energyFilename) {
                ;({ levels: energyLevelsStore, unit: energyUnit } =
                    await getYMLFileContents(energyFilename))
            } else {
                energyLevelsStore = []
            }

            energyLevelsStore = energyLevelsStore.map(setID)

            energyInfos[`${energyUnit}`] = energyLevelsStore

            if (energyUnit === 'cm-1') {
                energyInfos['MHz'] = energyLevelsStore.map(wavenumberToMHz)
            } else {
                energyInfos['cm-1'] = energyLevelsStore.map(MHzToWavenumber)
            }

            numberOfLevels = energyLevelsStore.length
            excitedFrom = energyLevelsStore?.[0].label
            excitedTo = energyLevelsStore?.[1].label

            if (einsteinFilename) {
                ;({ rateConstants: einsteinCoefficientA } =
                    await getYMLFileContents(einsteinFilename))
                einsteinCoefficientA = einsteinCoefficientA
                    .map(setID)
                    .map(correctObjValue)
            } else {
                einsteinCoefficientA = []
            }

            window.createToast('CONFIG loaded')
            console.log({
                energyLevels,
                collisionalCoefficient,
                einsteinCoefficientA,
            })
            updatePower()
            updateDoppler()
            updateEnergyLevels()
            configLoaded = true
        } catch (error) {
            window.handleError(error)
        }
    }

    let boltzmanWindow
    let openBoltzmanWindow = false

    $: voigtFWHM = Number(
        0.5346 * lorrentz + Math.sqrt(0.2166 * lorrentz ** 2 + gaussian ** 2)
    ).toFixed(3)

    let simulationMethod = 'Normal'
    const figure = { dpi: 100, size: '10, 6', show: true }
    const simulationMethods = [
        'Normal',
        'FixedPopulation',
        'withoutCollisionalConstants',
    ]

    const wavenumberToMHz = (energy) => ({
        ...energy,
        value: Number(energy.value * SpeedOfLight * 1e2 * 1e-6).toFixed(3),
    })
    const MHzToWavenumber = (energy) => ({
        ...energy,
        value: Number(energy.value / (SpeedOfLight * 1e2 * 1e-6)).toFixed(3),
    })

    $: energyLevels = energyInfos[`${energyUnit}`]
</script>

<BoltzmanDistribution
    {...boltzmanArgs}
    bind:active={openBoltzmanWindow}
    bind:graphWindow={boltzmanWindow}
/>

<LayoutDiv id="ROSAA__modal">
    <svelte:fragment slot="header_content__slot">
        <div
            class="locationColumn box v-center"
            style="border: solid 1px #fff9;"
        >
            <button
                class="button is-link"
                id="thz_modal_filebrowser_btn"
                on:click={browse_folder}>Browse</button
            >
            <Textfield bind:value={currentLocation} label="CONFIG location" />
            <Textfield bind:value={configFilename} label="CONFIG file" />
        </div>

        <div class="align box" style="border: solid 1px #fff9;">
            <CustomCheckbox
                bind:selected={includeCollision}
                label="includeCollision"
            />
            <CustomCheckbox
                bind:selected={includeAttachmentRate}
                label="includeAttachmentRate"
            />
            <CustomCheckbox
                bind:selected={includeSpontaneousEmission}
                label="includeSpontaneousEmission"
            />
            <CustomCheckbox
                bind:selected={electronSpin}
                label="Electron Spin"
            />
            <CustomCheckbox bind:selected={zeemanSplit} label="Zeeman" />
        </div>

        <div
            class="align box"
            style="border: solid 1px #fff9; min-height: 5em;"
        >
            <div class="subtitle">
                Simulate signal(%) as a function of {variable}
            </div>
            <div class="align v-center" style="width: auto; margin-left: auto;">
                {#if variable !== 'time'}
                    <Textfield
                        bind:value={variableRange}
                        style="width: auto;"
                        label="min, max, rangesteps:[1e1 format]"
                    />
                {/if}
                <CustomSelect
                    options={variablesList}
                    bind:picked={variable}
                    label="variable"
                />
                <button class="button is-link" on:click={loadConfig}
                    >Load config</button
                >
                <button class="button is-link" on:click={resetConfig}
                    >Reset Config</button
                >
            </div>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">
        <div
            class="content status_report__div"
            id="status_report__ROSAA"
            class:hide={!showreport}
        >
            <hr />
            {statusReport || 'Status report'}
            <hr />
        </div>

        <div class="main_container__div" class:hide={showreport}>
            <!-- Main Parameters -->

            <BoxComponent
                title="Main Parameters"
                loaded={mainParameters.length > 0}
            >
                {#each mainParameters as { label, value, id } (id)}
                    <Textfield bind:value {label} />
                {/each}
            </BoxComponent>

            <!-- Energy levels -->

            <BoxComponent
                title="Energy Levels"
                loaded={energyLevels.length > 0}
            >
                <svelte:fragment slot="control">
                    <Textfield
                        bind:value={numberOfLevels}
                        input$step={1}
                        input$min={0}
                        input$type={'number'}
                        label="numberOfLevels (J levels)"
                    />
                    <CustomSelect
                        options={['MHz', 'cm-1']}
                        bind:picked={energyUnit}
                        label="energyUnit"
                    />
                    <button
                        class="button is-link"
                        on:click={() => {
                            openBoltzmanWindow = true
                            setTimeout(() => boltzmanWindow?.focus(), 100)
                        }}
                    >
                        Show Boltzman distribution
                    </button>
                </svelte:fragment>

                {#each energyLevels as { label, value, id } (id)}
                    <Textfield bind:value {label} />
                {/each}
            </BoxComponent>

            <!-- Simulation parameters -->

            <BoxComponent
                title="Simulation parameters"
                loaded={simulationParameters.length > 0}
            >
                {#each simulationParameters as { label, value, id } (id)}
                    <Textfield bind:value {label} />
                {/each}

                <hr />
                <div
                    class="subtitle"
                    style="width: 100%; display:grid; place-items: center;"
                >
                    Transition levels
                </div>
                <hr />
                <div class="align h-center">
                    <CustomSelect
                        options={energyLevels.map((f) => f.label)}
                        bind:picked={excitedFrom}
                        label="excitedFrom"
                        on:change={updateEnergyLevels}
                    />
                    <CustomSelect
                        options={energyLevels.map((f) => f.label)}
                        bind:picked={excitedTo}
                        label="excitedTo"
                        on:change={updateEnergyLevels}
                    />
                    <Textfield
                        value={Number(upperLevelEnergy - lowerLevelEnergy) || 0}
                        label="transitionFrequency ({energyUnit})"
                    />
                </div>
            </BoxComponent>

            <!-- Doppler lineshape -->

            <BoxComponent
                title="Doppler lineshape"
                loaded={dopplerLineshape.length > 0}
            >
                {#each dopplerLineshape as { label, value, id } (id)}
                    <CustomTextSwitch step={0.5} bind:value {label} />
                {/each}
                <Textfield
                    bind:value={collisionalTemp}
                    label="collisionalTemp(K)"
                />
                <Textfield
                    bind:value={gaussian}
                    label="gaussian - FWHM (MHz)"
                />
            </BoxComponent>

            <!-- Lorrentz lineshape -->

            <BoxComponent
                title="Lorrentz lineshape"
                loaded={powerBroadening.length > 0}
            >
                {#each powerBroadening as { label, value, id } (id)}
                    <Textfield bind:value {label} />
                {/each}
                <Textfield
                    bind:value={lorrentz}
                    label="lorrentz - FWHM (MHz)"
                />
                <Textfield
                    value={voigtFWHM}
                    label="Voigt - FWHM (MHz)"
                    variant="outlined"
                />
            </BoxComponent>

            <EinsteinCoefficients
                bind:einsteinCoefficientA
                bind:einsteinCoefficientB
                bind:einsteinB_rateComputed
                bind:einsteinCoefficientB_rateConstant
                {power}
                {gaussian}
                {trapArea}
                {lorrentz}
                {energyUnit}
                {zeemanSplit}
                {electronSpin}
                {energyLevels}
                {configLoaded}
            />

            <CollisionalCoefficients
                bind:numberDensity
                bind:collisionalRates
                bind:collisionalCoefficient
                bind:collisionalCoefficient_balance
                {energyUnit}
                {zeemanSplit}
                {electronSpin}
                {energyLevels}
                {collisionalTemp}
                {collisionalFilename}
                {numberOfLevels}
            />

            <AttachmentCoefficients
                bind:k3
                bind:kCID
                bind:numberDensity
                bind:attachmentCoefficients
            />

            <!-- Figure config -->

            <BoxComponent title="Figure config" loaded={true}>
                <Textfield
                    bind:value={figure.size}
                    label="Dimention (width, height)"
                />

                <Textfield bind:value={figure.dpi} label="DPI" />
                <CustomCheckbox
                    bind:selected={figure.show}
                    label="show figure"
                />
            </BoxComponent>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="left_footer_content__slot">
        <CustomCheckbox bind:selected={writefile} label="writefile" />
        <CustomCheckbox bind:selected={writeall} label="writeall" />
        <CustomCheckbox bind:selected={appendFiles} label="appendFiles" />
        <Textfield bind:value={savefilename} label="savefilename" />
    </svelte:fragment>

    <svelte:fragment slot="footer_content__slot">
        <!-- {#if pyProcesses.length>0}
        
            <div>{'Running:'+ pyProcesses.length}</div>
            <button transition:fade class="button is-danger" 
                on:click="{()=>{pyProcesses.at(-1).kill(); pyProcesses.pop()}}" >Stop</button>
        {/if} -->

        <CustomSelect
            options={simulationMethods}
            bind:picked={simulationMethod}
            label="simulationMethod"
        />
        {#if showreport}
            <button
                class="button is-warning"
                on:click={() => {
                    statusReport = ''
                }}>Clear</button
            >
        {/if}
        <button
            class="button is-link"
            on:click={() => {
                showreport = !showreport
            }}
        >
            {showreport ? 'Go Back' : 'Status report'}
        </button>

        <!-- <PyButton on:click={simulation} bind:pyProcesses bind:stdOutput={statusReport} /> -->
        <button class="button is-link" on:click={simulation}>Submit</button>
    </svelte:fragment>
</LayoutDiv>

<style lang="scss">
    .locationColumn {
        display: grid;
        grid-auto-flow: column;

        grid-gap: 1em;
        grid-template-columns: 0.5fr 4fr 1fr;
    }

    .main_container__div {
        display: grid;
        grid-row-gap: 1em;
        padding-right: 1em;
    }

    .status_report__div {
        white-space: pre-wrap;
        user-select: text;
    }

    .box {
        padding: 0.5em 1.25em;
    }
</style>
