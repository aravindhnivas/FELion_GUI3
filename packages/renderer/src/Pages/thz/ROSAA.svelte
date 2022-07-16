<script lang="ts">
    import Textfield from '@smui/textfield'
    import { parse as Yml } from 'yaml'
    import { browse } from '$components/Layout.svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import LayoutDiv from '$components/LayoutDiv.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import ButtonBadge from '$components/ButtonBadge.svelte'
    import BoltzmanDistribution from './windows/BoltzmanDistribution.svelte'
    import EinsteinCoefficients from './components/EinsteinCoefficients.svelte'
    import CollisionalCoefficients from './components/CollisionalCoefficients.svelte'
    import AttachmentCoefficients from './components/AttachmentCoefficients.svelte'
    import Accordion from '@smui-extra/accordion'
    import CustomPanel from '$components/CustomPanel.svelte'
    import SeparateWindow from '$components/SeparateWindow.svelte'
    import {
        amuToKG,
        DebyeToCm,
        SpeedOfLight,
        PlanksConstant,
        boltzmanConstant,
        VaccumPermitivity,
    } from '$src/js/constants'
    import computePy_func from '$src/Pages/general/computePy'
    import { persistentWritable } from '$src/js/persistentStore'
    import { tick } from 'svelte'
    //////////////////////////////////////////////////////////////////////////////////////////////////////////

    let electronSpin = false
    let zeemanSplit = false

    let [mainParameters, simulationParameters, dopplerLineshape, powerBroadening] = Array(4).fill([])

    let k3 = { constant: [], rate: [] }
    let kCID = { constant: [], rate: [] }
    let attachmentCoefficients = []

    let collisionalRateType = 'excitation'
    $: deexcitation = collisionalRateType === 'deexcitation'

    let showreport = false
    let statusReport = ''

    let collisionalRates = []
    let collisionalRateConstants = []
    let einsteinB_rateComputed = false

    const simulation = async (e) => {
        // progress = 0
        if (!window.fs.existsSync(currentLocation)) return window.createToast("Location doesn't exist", 'danger')
        if (!configLoaded) return window.createToast('Config file not loaded', 'danger')
        if (!transitionFrequency) return window.createToast('Transition frequency is not defined', 'danger')
        if (!einsteinB_rateComputed) return window.createToast('Compute einsteinB rate constants', 'danger')

        if (includeCollision) {
            collisionalRateConstants = [...collisionalCoefficient, ...collisionalCoefficient_balance]
            if (collisionalRateConstants.length < 1)
                return window.createToast('Compute collisional rate constants', 'danger')
        }

        if (includeAttachmentRate) {
            if (k3.constant.length < 1) return window.createToast('Compute attachment rate constants', 'danger')
        }

        const collisional_rates = {}
        collisionalRateConstants.forEach((f) => (collisional_rates[f.label] = f.value))

        const main_parameters = {}
        mainParameters.forEach((f) => (main_parameters[f.label] = f.value))

        const simulation_parameters = {}
        simulationParameters.forEach((f) => (simulation_parameters[f.label] = f.value))

        const lineshape_conditions = {}
        dopplerLineshape.forEach((f) => (lineshape_conditions[f.label] = f.value))

        const power_broadening = {}
        powerBroadening.forEach((f) => (power_broadening[f.label] = f.value))

        const einstein_coefficient = { A: {}, B: {}, B_rateConstant: {} }
        einsteinCoefficientA.forEach((f) => (einstein_coefficient.A[f.label] = f.value))
        einsteinCoefficientB.forEach((f) => (einstein_coefficient.B[f.label] = f.value))
        einsteinCoefficientB_rateConstant.forEach((f) => (einstein_coefficient.B_rateConstant[f.label] = f.value))

        const attachment_rate_coefficients = {
            rateConstants: {
                k3: k3.constant.map((rate) => rate.value),
                kCID: kCID.constant.map((rate) => rate.value),
            },
        }
        attachmentCoefficients.forEach((f) => (attachment_rate_coefficients[f.label] = f.value))
        const energy_levels = {}
        energyLevels.slice(0, numberOfLevels).forEach((f) => (energy_levels[f.label] = f.value))
        const args = {
            trapTemp,
            variable,
            $variableRange,
            numberOfLevels,
            includeCollision,
            includeAttachmentRate,
            gaussian,
            lorrentz,
            includeSpontaneousEmission,
            writefile,
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
        statusReport = ''
        await computePy_func({ e, pyfile: 'ROSAA', args, general: true })
        progress = 0
    }

    let currentLocation = window.fs.existsSync(window.db.get('ROSAA_config_location'))
        ? <string>window.db.get('ROSAA_config_location')
        : ''

    let moleculeName = ''
    let tagName = 'He'

    $: savefilename = `${moleculeName}_${tagName}_f-${variable.split('(')[0]}__transition_${excitedFrom}-${excitedTo}`
        .replaceAll('$', '')
        .replaceAll('^', '')

    $: if (window.fs.isDirectory(currentLocation)) {
        window.db.set('ROSAA_config_location', currentLocation)
    }

    async function browse_folder() {
        const [result] = await browse({ filetype: 'yml', dir: false })
        console.log(result)
        if (!result) return
        configFilename = window.path.basename(result)
        currentLocation = window.path.dirname(result)
        window.db.set('ROSAA_config_location', currentLocation)
        window.db.set('ROSAA_config_file', configFilename)
    }

    const resetConfig = () => {
        einsteinCoefficientA = einsteinCoefficientB = []
        energyLevels = []
        simulationParameters = mainParameters = dopplerLineshape = powerBroadening = []
        attachmentCoefficients = []
        window.createToast('Config file cleared', 'warning')
    }
    let writefile = true
    let includeCollision = true
    let includeAttachmentRate = true

    let includeSpontaneousEmission = true
    let variable = 'time'

    const variableRange = persistentWritable('THz_simulation_variables_range', {
        power: '1e-7, 1e-2, 10',
        numberDensity: '1e12, 1e16, 10',
        k3_branch: '0.1, 1, 0.1',
    })

    const variablesList = ['time', 'He density(cm3)', 'Power(W)', 'a(k_up/k_down)', 'all']

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

    $: configFile = window.path.join(currentLocation, configFilename)
    $: boltzmanArgs = {
        energyLevels,
        trapTemp,
        electronSpin,
        zeemanSplit,
        energyUnit,
    }

    let configLoaded = false
    let collisionalCoefficient_balance = []
    let configFilename = <string>window.db.get('ROSAA_config_file') || ''
    async function loadConfig() {
        try {
            console.log({ configFile })
            if (window.fs.isFile(configFile)) {
                await setConfig()
                await tick()
                return
            }
            browse_folder()
        } catch (error) {
            window.handleError(error)
        }
    }

    const getYMLFileContents = (filename) => {
        if (window.fs.existsSync(filename)) {
            const fileContent = window.fs.readFileSync(filename)
            const YMLcontent = Yml(fileContent)
            return Promise.resolve(YMLcontent)
        } else return Promise.reject(filename + " file doesn't exist")
    }

    const setID = (obj) => ({ ...obj, id: window.getID() })
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

    let ionMass = 14
    let RGmass = 4
    let ionTemp = 12
    let trapTemp = 5
    let gaussian = 0
    let collisionalTemp: number = null
    let Cg = 0 // doppler-broadening proportionality constant

    let power = '2e-5'
    let dipole = 1
    let lorrentz = 0
    let Cp = 0 // power-broadening proportionality constant

    $: console.log(mainParameters)
    const updateEnergyLevels = () => {
        console.log('energyLevels updated')
        if (!energyLevels) return console.warn('No energyLevels defined', energyLevels)
        console.log(energyLevels)
        lowerLevelEnergy = energyLevels?.filter((energy) => energy.label == excitedFrom)?.[0]?.value || 0
        upperLevelEnergy = energyLevels?.filter((energy) => energy.label == excitedTo)?.[0]?.value || 0

        transitionFrequency = upperLevelEnergy - lowerLevelEnergy
        if (energyUnit == 'cm-1') {
            transitionFrequency *= SpeedOfLight * 1e2 * 1e-6
        }
        updateDoppler()
    }

    const updateDoppler = () => {
        console.log('Changing doppler parameters')
        ;[ionMass, RGmass, ionTemp, trapTemp] = dopplerLineshape.map((f) => Number(f.value))

        collisionalTemp = Number(Number((RGmass * ionTemp + ionMass * trapTemp) / (ionMass + RGmass)).toFixed(1))
        const sqrtTerm = (8 * boltzmanConstant * Math.log(2) * ionTemp) / (ionMass * amuToKG * SpeedOfLight ** 2)
        Cg = Math.sqrt(sqrtTerm)
        gaussian = Number(Number(transitionFrequency * Cg).toFixed(3)) // in MHz
    }
    const updatePower = () => {
        ;[dipole, power] = powerBroadening.map((f) => Number(f.value))
        trapArea = mainParameters?.filter((params) => params.label === 'trap_area (sq-meter)')?.[0]?.value || ''
        Cp = ((2 * dipole * DebyeToCm) / PlanksConstant) * Math.sqrt(1 / (trapArea * SpeedOfLight * VaccumPermitivity))
        lorrentz = Number(Number(Cp * Math.sqrt(Number(power)) * 1e-6).toFixed(3))
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
            const configFileLocation = window.path.dirname(configFile)
            const CONFIG = Yml(window.fs.readFileSync(configFile))
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
            k3.constant = attachmentRateConstants.k3.map(setID).map(correctObjValue)
            kCID.constant = attachmentRateConstants.kCID.map(setID).map(correctObjValue)
            ;({ trapTemp, zeemanSplit, electronSpin, numberDensity } = CONFIG)
            // ({savefilename}         = CONFIG.saveFile);
            moleculeName = mainParameters.filter((params) => params.label == 'molecule')?.[0]?.value || ''
            tagName = mainParameters?.filter((params) => params.label == 'tagging partner')?.[0]?.value || ''
            const { savelocation } = CONFIG.saveFile
            if (window.fs.existsSync(savelocation)) {
                currentLocation = savelocation
            }

            ;({
                energy: energyFilename,
                einsteinA: einsteinFilename,
                collision: collisionalFilename,
            } = CONFIG.filenames)
            energyFilename = energyFilename ? window.path.join(configFileLocation, 'files', energyFilename) : ''
            einsteinFilename = einsteinFilename ? window.path.join(configFileLocation, 'files', einsteinFilename) : ''
            collisionalFilename = collisionalFilename
                ? window.path.join(configFileLocation, 'files', collisionalFilename)
                : ''

            let energyLevelsStore = []

            if (energyFilename) {
                ;({ levels: energyLevelsStore, unit: energyUnit } = await getYMLFileContents(energyFilename))
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
                ;({ rateConstants: einsteinCoefficientA } = await getYMLFileContents(einsteinFilename))
                einsteinCoefficientA = einsteinCoefficientA.map(setID).map(correctObjValue)
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
            updateEnergyLevels()
            configLoaded = true
            return Promise.resolve('config loaded')
        } catch (error) {
            window.handleError(error)
            return Promise.reject(error)
        }
    }

    let boltzmanWindow
    let openBoltzmanWindow = false
    $: voigtFWHM = Number(0.5346 * lorrentz + Math.sqrt(0.2166 * lorrentz ** 2 + gaussian ** 2)).toFixed(3)
    let simulationMethod = 'Normal'
    const figure = { dpi: 100, size: '10, 6', show: true }
    const simulationMethods = ['Normal', 'FixedPopulation', 'withoutCollisionalConstants']
    const wavenumberToMHz = (energy) => ({
        ...energy,
        value: Number(energy.value * SpeedOfLight * 1e2 * 1e-6).toFixed(3),
    })
    const MHzToWavenumber = (energy) => ({
        ...energy,
        value: Number(energy.value / (SpeedOfLight * 1e2 * 1e-6)).toFixed(3),
    })

    $: energyLevels = energyInfos[`${energyUnit}`]
    let toggle_modal = false
    let progress = 0
</script>

<BoltzmanDistribution
    {...boltzmanArgs}
    bind:active={openBoltzmanWindow}
    bind:graphWindow={boltzmanWindow}
    {currentLocation}
/>

<LayoutDiv id="ROSAA__modal" {progress} showProgress={true}>
    <svelte:fragment slot="header_content__slot">
        <div class="locationColumn box v-center" style="border: solid 1px #fff9;">
            <button class="button is-link" id="thz_modal_filebrowser_btn" on:click={browse_folder}>Browse</button>
            <Textfield bind:value={currentLocation} label="CONFIG location" />
            <Textfield bind:value={configFilename} label="CONFIG file" />
        </div>

        <div class="align box" style="border: solid 1px #fff9;">
            <CustomCheckbox bind:value={includeCollision} label="includeCollision" />
            <CustomCheckbox bind:value={includeAttachmentRate} label="includeAttachmentRate" />
            <CustomCheckbox bind:value={includeSpontaneousEmission} label="includeSpontaneousEmission" />
            <CustomCheckbox bind:value={electronSpin} label="Electron Spin" />
            <CustomCheckbox bind:value={zeemanSplit} label="Zeeman" />
        </div>

        <div class="align box" style="border: solid 1px #fff9; min-height: 5em;">
            <div class="align subtitle">
                Simulate signal(%) as a function of {variable}
            </div>
            <div class="align v-center" style="width: auto; margin-left: auto;">
                {#if variable !== 'time'}
                    <Textfield
                        class={variable === 'all' || variable === 'a(k_up/k_down)' ? '' : 'hide'}
                        bind:value={$variableRange.k3_branch}
                        style="width: auto;"
                        label="a: (min, max, steps)"
                    />
                    <Textfield
                        class={variable === 'all' || variable === 'Power(W)' ? '' : 'hide'}
                        bind:value={$variableRange.power}
                        style="width: auto;"
                        label="P: (min, max, steps)"
                    />
                    <Textfield
                        class={variable === 'all' || variable === 'He density(cm3)' ? '' : 'hide'}
                        bind:value={$variableRange.numberDensity}
                        style="width: auto;"
                        label="nHe: (min, max, steps)"
                    />
                {/if}
                <CustomSelect options={variablesList} bind:value={variable} label="variable" />
                <button class="button is-link" on:click={loadConfig}>Load config</button>
                <button class="button is-link" on:click={resetConfig}>Reset Config</button>
                <button class="button is-warning" on:click={() => (toggle_modal = !toggle_modal)}
                    >Open separately</button
                >
            </div>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">
        <SeparateWindow
            bind:active={toggle_modal}
            title="ROSAA controller"
            graphMode={false}
            autoHide={false}
            mainContent$style=""
        >
            <svelte:fragment slot="main_content__slot">
                <div
                    class="align status_report__div p-5"
                    id="THz_simulation_status"
                    style="user-select: text;"
                    class:hide={!showreport}
                >
                    {statusReport}
                </div>
                <div class="main_container__div" class:hide={showreport}>
                    <!-- Main Parameters -->
                    <Accordion multiple style="width: 100%;">
                        <CustomPanel label="Main Parameters" loaded={mainParameters.length > 0}>
                            <div class="align h-center">
                                {#each mainParameters as { label, value, id } (id)}
                                    <Textfield bind:value {label} />
                                {/each}
                            </div>
                        </CustomPanel>

                        <!-- Energy levels -->
                        <CustomPanel label="Energy Levels" loaded={energyLevels.length > 0}>
                            <div class="align h-center">
                                <Textfield
                                    bind:value={numberOfLevels}
                                    input$step={1}
                                    input$min={0}
                                    type={'number'}
                                    label="numberOfLevels (J levels)"
                                />
                                <CustomSelect options={['MHz', 'cm-1']} bind:value={energyUnit} label="energyUnit" />
                                <button
                                    class="button is-link"
                                    on:click={() => {
                                        openBoltzmanWindow = true
                                        setTimeout(() => boltzmanWindow?.focus(), 100)
                                    }}
                                >
                                    Show Boltzman distribution
                                </button>
                            </div>

                            <div class="align h-center">
                                {#each energyLevels as { label, value, id } (id)}
                                    <Textfield bind:value {label} />
                                {/each}
                            </div>
                        </CustomPanel>

                        <!-- Simulation parameters -->
                        <CustomPanel label="Simulation parameters" loaded={simulationParameters.length > 0}>
                            <div class="align h-center mb-5">
                                {#each simulationParameters as { label, value, id } (id)}
                                    <Textfield bind:value {label} />
                                {/each}
                            </div>

                            <div class="align h-center">
                                <CustomSelect
                                    options={energyLevels.map((f) => f.label)}
                                    bind:value={excitedFrom}
                                    label="excitedFrom"
                                    on:change={updateEnergyLevels}
                                />
                                <CustomSelect
                                    options={energyLevels.map((f) => f.label)}
                                    bind:value={excitedTo}
                                    label="excitedTo"
                                    on:change={updateEnergyLevels}
                                />
                                <Textfield
                                    value={Number(upperLevelEnergy - lowerLevelEnergy) || 0}
                                    label="transitionFrequency ({energyUnit})"
                                />
                            </div>
                        </CustomPanel>

                        <!-- Doppler lineshape -->
                        <CustomPanel label="Doppler lineshape" loaded={dopplerLineshape.length > 0}>
                            {#each dopplerLineshape as { label, value, id } (id)}
                                <CustomTextSwitch step={0.5} bind:value {label} />
                            {/each}
                            <Textfield
                                bind:value={collisionalTemp}
                                label="collisionalTemp(K)"
                                type="number"
                                input$step="0.1"
                            />
                            <Textfield bind:value={gaussian} label="gaussian - FWHM (MHz)" />
                        </CustomPanel>

                        <!-- Lorrentz lineshape -->
                        <CustomPanel label="Lorrentz lineshape" loaded={powerBroadening.length > 0}>
                            {#each powerBroadening as { label, value, id } (id)}
                                <Textfield bind:value {label} />
                            {/each}
                            <Textfield bind:value={lorrentz} label="lorrentz - FWHM (MHz)" />
                            <Textfield value={voigtFWHM} label="Voigt - FWHM (MHz)" variant="outlined" />
                        </CustomPanel>

                        <CustomPanel
                            label="Einstein Co-efficients"
                            loaded={einsteinCoefficientA.length > 0 &&
                                einsteinCoefficientB.length > 0 &&
                                einsteinB_rateComputed}
                        >
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
                            />
                        </CustomPanel>

                        <CustomPanel label="Collisional rate constants" loaded={collisionalFilename?.length > 0}>
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
                        </CustomPanel>

                        <CustomPanel
                            label="Rare-gas attachment (K3) and dissociation (kCID) constants"
                            loaded={attachmentCoefficients.length > 0}
                        >
                            <AttachmentCoefficients bind:k3 bind:kCID bind:numberDensity bind:attachmentCoefficients />
                        </CustomPanel>
                    </Accordion>
                </div>
            </svelte:fragment>
        </SeparateWindow>
    </svelte:fragment>

    <svelte:fragment slot="left_footer_content__slot">
        <CustomCheckbox bind:value={writefile} label="writefile" />
        <Textfield bind:value={savefilename} label="savefilename" />
        <CustomCheckbox bind:value={figure.show} label="show figure" />
    </svelte:fragment>

    <svelte:fragment slot="footer_content__slot">
        <button
            style="align-self:end;"
            class="button is-danger"
            class:hide={!showreport}
            on:click={() => {
                statusReport = ''
            }}>clear</button
        >
        <button
            style="align-self:end;"
            class="button is-warning"
            on:click={() => {
                showreport = !showreport
            }}>{showreport ? 'Go back' : 'Show report'}</button
        >
        <div style="display: flex; gap: 1em;" class:hide={showreport}>
            <CustomSelect options={simulationMethods} bind:value={simulationMethod} label="simulationMethod" />
            <ButtonBadge
                on:pyEventData={async (e) => {
                    const { stdout } = e.detail
                    statusReport += stdout
                    if (stdout.includes('%')) {
                        const percent = parseFloat(stdout.split('%')[0].trim())
                        // console.log(percent)

                        if (percent > 0) {
                            progress = percent / 100
                        }
                    }
                    await tick()
                    document.getElementById('THz_simulation_status').scrollIntoView(false)
                }}
                on:click={simulation}
                style="align-self:end;"
            />
        </div>
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
    .box {
        padding: 0.5em 1.25em;
    }
    .status_report__div {
        white-space: pre-wrap;
    }
</style>
