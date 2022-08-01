<script lang="ts">
    import { energyLevels, numberOfLevels, energyUnit, transitionFrequency } from './stores/energy'
    import { einsteinCoefficientA, einsteinCoefficientB, einsteinCoefficientB_rateConstant } from './stores/einstein'
    import {
        electronSpin,
        zeemanSplit,
        currentLocation,
        excitedFrom,
        excitedTo,
        trapTemp,
        configFile,
    } from './stores/common'
    import { collisionalRateConstants } from './stores/collisional'
    import { tick } from 'svelte'
    import Textfield from '@smui/textfield'
    import Accordion from '@smui-extra/accordion'
    import { parse as Yml } from 'yaml'
    import CustomSelect from '$components/CustomSelect.svelte'
    import LayoutDiv from '$components/LayoutDiv.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import EinsteinCoefficients from './components/EinsteinCoefficients.svelte'
    import CollisionalCoefficients from './components/CollisionalCoefficients.svelte'
    import AttachmentCoefficients from './components/AttachmentCoefficients.svelte'
    import ROSAA_Footer from './ROSAA_layout/ROSAA_Footer.svelte'
    import CustomPanel from '$components/CustomPanel.svelte'
    import SeparateWindow from '$components/SeparateWindow.svelte'
    import EnergyDetails from './components/EnergyDetails.svelte'
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
    import { setID, correctObjValue, getYMLFileContents } from '$src/js/utils'
    import BrowseTextfield from '$src/components/BrowseTextfield.svelte'
    import VariableSelector from './components/header/VariableSelector.svelte'
    //////////////////////////////////////////////////////////////////////////////////////////////////////////

    let [mainParameters, simulationParameters, dopplerLineshape, powerBroadening]: Coefficients[] = Array(4).fill([])

    let k3: AttachmentRate = { constant: [], rate: [] }
    let kCID: AttachmentRate = { constant: [], rate: [] }
    let attachmentCoefficients: Coefficients = []

    let collisionalRateType = 'excitation'
    $: deexcitation = collisionalRateType === 'deexcitation'

    let showreport = false
    let statusReport = ''

    const simulation = async (e?: Event) => {
        if (!window.fs.isDirectory($currentLocation)) return window.createToast("Location doesn't exist", 'danger')
        if (!configLoaded) return window.createToast('Config file not loaded', 'danger')
        if (!$transitionFrequency) return window.createToast('Transition frequency is not defined', 'danger')

        if (includeCollision) {
            if ($collisionalRateConstants.length < 1)
                return window.createToast('Compute collisional rate constants', 'danger')
        }

        if (includeAttachmentRate) {
            if (k3.constant.length < 1) return window.createToast('Compute attachment rate constants', 'danger')
        }

        const collisional_rates: KeyStringObj = {}
        $collisionalRateConstants.forEach((f) => (collisional_rates[f.label] = f.value))

        const main_parameters: KeyStringObj = {}
        mainParameters.forEach((f) => (main_parameters[f.label] = f.value))

        const simulation_parameters: KeyStringObj = {}
        simulationParameters.forEach((f) => (simulation_parameters[f.label] = f.value))

        const lineshape_conditions: KeyStringObj = {}
        dopplerLineshape.forEach((f) => (lineshape_conditions[f.label] = f.value))

        const power_broadening: KeyStringObj = {}
        powerBroadening.forEach((f) => (power_broadening[f.label] = f.value))

        const einstein_coefficient: {
            [key in 'A' | 'B' | 'B_rateConstant']: KeyStringObj
        } = { A: {}, B: {}, B_rateConstant: {} }

        $einsteinCoefficientA.forEach((f) => (einstein_coefficient.A[f.label] = f.value))
        $einsteinCoefficientB.forEach((f) => (einstein_coefficient.B[f.label] = f.value))
        $einsteinCoefficientB_rateConstant.forEach((f) => (einstein_coefficient.B_rateConstant[f.label] = f.value))

        const attachment_rate_coefficients = {
            rateConstants: {
                k3: k3.constant.map((rate) => rate.value),
                kCID: kCID.constant.map((rate) => rate.value),
            },
        }

        attachmentCoefficients.forEach((f) => (attachment_rate_coefficients[f.label] = f.value))

        const energy_levels: KeyStringObj<number> = {}
        $energyLevels.slice(0, $numberOfLevels).forEach((f) => (energy_levels[f.label] = f.value))

        const keys = <const>['k3_branch', 'numberDensity', 'power']
        for (const key of keys) {
            const values = $variableRange[key].split(',').map((v) => parseFloat(v))
            console.log(values)
            if (values.length < 3) {
                window.handleError(
                    `Variable range for ${key} is not defined properly. It should be a comma separated list of 3 values.`
                )
                return
            }
        }

        const args = {
            trapTemp: $trapTemp,
            variable,
            $variableRange,
            numberOfLevels: $numberOfLevels,
            includeCollision,
            includeAttachmentRate,
            gaussian,
            lorrentz,
            includeSpontaneousEmission,
            writefile,
            savefilename,
            currentLocation: $currentLocation,
            deexcitation,
            collisional_rates,
            main_parameters,
            simulation_parameters,
            einstein_coefficient,
            energy_levels,
            energyUnit: $energyUnit,
            power_broadening,
            lineshape_conditions,
            attachment_rate_coefficients,
            electronSpin: $electronSpin,
            zeemanSplit: $zeemanSplit,
            excitedFrom: $excitedFrom,
            excitedTo: $excitedTo,
            numberDensity,
            collisionalTemp,
            simulationMethod,
            figure,
        }
        progress = 0
        showProgress = true
        statusReport = ''
        await computePy_func({ e, pyfile: 'ROSAA', args, general: true })
    }
    let moleculeName = ''
    let tagName = 'He'

    $: savefilename = `${moleculeName}_${tagName}_f-${variable.split('(')[0]}__transition_${$excitedFrom}-${$excitedTo}`
        .replaceAll('$', '')
        .replaceAll('^', '')

    function browse_folder() {
        const [result] = window.browse({ filetype: 'yml', dir: false })
        if (!result) return
        $configFile = result
    }

    const resetConfig = () => {
        $einsteinCoefficientA = $einsteinCoefficientB = []
        $energyLevels = []
        simulationParameters = mainParameters = dopplerLineshape = powerBroadening = []
        attachmentCoefficients = []
        window.createToast('Config file cleared', 'warning')
    }

    let writefile = true

    let includeCollision = true
    let includeAttachmentRate = true
    let includeSpontaneousEmission = true
    let variable = 'time'

    const variableRange: VariableOptions = persistentWritable('THz_simulation_variables_range', {
        power: '1e-7, 1e-2, 50',
        numberDensity: '1e12, 1e16, 50',
        k3_branch: '0.1, 1, 0.1',
    })

    const variablesList = ['time', 'He density(cm-3)', 'Power(W)', 'a(k_up/k_down)', 'all']

    let numberDensity = '2e14'
    let energyFilename: string
    let einsteinFilename: string
    let collisionalFilename: string

    let configLoaded = false
    // let configFilename = <string>window.db.get('ROSAA_config_file') || ''
    async function loadConfig() {
        try {
            if (window.fs.isFile($configFile)) {
                await setConfig()
                await tick()
                return
            }
            browse_folder()
        } catch (error) {
            window.handleError(error)
        }
    }

    let trapArea: string
    let ionMass = 14
    let RGmass = 4
    let ionTemp = 12
    let gaussian = 0

    let collisionalTemp: number = 5
    let Cg = 0 // doppler-broadening proportionality constant
    let power: string | number = '2e-5'
    let dipole = 1
    let lorrentz = 0
    let Cp = 0 // power-broadening proportionality constant

    const updateDoppler = () => {
        console.log('Changing doppler parameters')
        ;[ionMass, RGmass, ionTemp, $trapTemp] = dopplerLineshape.map((f) => Number(f.value))

        collisionalTemp = Number(Number((RGmass * ionTemp + ionMass * $trapTemp) / (ionMass + RGmass)).toFixed(1))
        const sqrtTerm = (8 * boltzmanConstant * Math.log(2) * ionTemp) / (ionMass * amuToKG * SpeedOfLight ** 2)
        Cg = Math.sqrt(sqrtTerm)
        gaussian = Number(Number($transitionFrequency * Cg).toFixed(3)) // in MHz
    }
    const updatePower = () => {
        console.log({ powerBroadening, trapArea })
        ;[dipole, power] = powerBroadening.map((f) => Number(f.value))
        trapArea = mainParameters?.filter((params) => params.label === 'trap_area (sq-meter)')?.[0]?.value || ''
        Cp =
            ((2 * dipole * DebyeToCm) / PlanksConstant) *
            Math.sqrt(1 / (Number(trapArea) * SpeedOfLight * VaccumPermitivity))
        lorrentz = Number(Number(Cp * Math.sqrt(Number(power)) * 1e-6).toFixed(3))
    }

    $: {
        if ($transitionFrequency || dopplerLineshape.length) {
            updateDoppler()
        }
        if (powerBroadening.length) {
            updatePower()
        }
    }

    let configsBaseName = 'files'

    async function setConfig() {
        try {
            const fileRead = window.fs.readFileSync($configFile)
            if (window.fs.isError(fileRead)) return window.handleError(fileRead)

            const CONFIG = Yml(fileRead)
            console.table(CONFIG)

            let attachmentRateConstants: {
                [key in 'k3' | 'kCID']: Omit<ValueLabel, 'id'>[]
            } = { k3: [], kCID: [] }

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
            ;({ trapTemp: $trapTemp, zeemanSplit: $zeemanSplit, electronSpin: $electronSpin, numberDensity } = CONFIG)
            // ({savefilename}         = CONFIG.saveFile);
            moleculeName = mainParameters.filter((params) => params.label == 'molecule')?.[0]?.value || ''
            tagName = mainParameters?.filter((params) => params.label == 'tagging partner')?.[0]?.value || ''
            // const { savelocation } = CONFIG.saveFile
            // if (window.fs.isDirectory(savelocation)) {
            //     $currentLocation = savelocation
            // }
            ;({
                energy: energyFilename,
                einsteinA: einsteinFilename,
                collision: collisionalFilename,
            } = CONFIG.filenames)

            if ('base' in CONFIG.filenames) {
                configsBaseName = CONFIG.filenames.base
            }

            energyFilename = energyFilename ? window.path.join($currentLocation, configsBaseName, energyFilename) : ''
            einsteinFilename = einsteinFilename
                ? window.path.join($currentLocation, configsBaseName, einsteinFilename)
                : ''
            collisionalFilename = collisionalFilename
                ? window.path.join($currentLocation, configsBaseName, collisionalFilename)
                : ''

            if (einsteinFilename) {
                const { rateConstants } = await getYMLFileContents(einsteinFilename)
                $einsteinCoefficientA = rateConstants.map(setID).map(correctObjValue)
            } else {
                $einsteinCoefficientA = []
            }
            window.createToast('CONFIG loaded')

            updatePower()
            updateDoppler()
            configLoaded = true
            return Promise.resolve('config loaded')
        } catch (error) {
            window.handleError(error)
            return Promise.reject(error)
        }
    }

    $: voigtFWHM = Number(0.5346 * lorrentz + Math.sqrt(0.2166 * lorrentz ** 2 + gaussian ** 2)).toFixed(3)
    let simulationMethod = 'Normal'
    const figure = { dpi: 100, size: '10, 6', show: true }

    let toggle_modal = false
    let progress = 0
    let showProgress = false
</script>

<LayoutDiv id="ROSAA__modal" {progress} bind:showProgress>
    <svelte:fragment slot="header_content__slot">
        <BrowseTextfield
            class="two_col_browse box"
            dir={false}
            filetype="yml"
            bind:value={$configFile}
            label="config file"
        />
        <div class="align box px-3 py-2" class:hide={showreport} style="border: solid 1px #fff9;">
            <CustomCheckbox bind:value={includeCollision} label="includeCollision" />
            <CustomCheckbox bind:value={includeAttachmentRate} label="includeAttachmentRate" />
            <CustomCheckbox bind:value={includeSpontaneousEmission} label="includeSpontaneousEmission" />
            <CustomCheckbox bind:value={$electronSpin} label="Electron Spin" />
            <CustomCheckbox bind:value={$zeemanSplit} label="Zeeman" />
        </div>

        <div class="align box px-3 py-2" class:hide={showreport} style="border: solid 1px #fff9; min-height: 5em;">
            <div class="align subtitle">
                Simulate signal(%) as a function of {variable}
            </div>
            <div class="align v-center" style="width: auto; margin-left: auto;">
                <CustomSelect options={variablesList} bind:value={variable} label="variable" />
                <button class="button is-link" on:click={loadConfig}>Load config</button>
                <button class="button is-link" on:click={resetConfig}>Reset Config</button>
                <button class="button is-warning" on:click={() => (toggle_modal = !toggle_modal)}
                    >Open separately</button
                >
            </div>

            <VariableSelector {variable} {variableRange} />
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
                    style="user-select: text; white-space: pre-wrap;"
                    class:hide={!showreport}
                >
                    {statusReport}
                </div>
                <div class="pr-5" class:hide={showreport}>
                    <Accordion multiple style="width: 100%;">
                        <CustomPanel label="Main Parameters" loaded={mainParameters.length > 0}>
                            <div class="align h-center">
                                {#each mainParameters as { label, value, id } (id)}
                                    <Textfield bind:value {label} />
                                {/each}
                            </div>
                        </CustomPanel>

                        <EnergyDetails bind:energyFilename />

                        <CustomPanel label="Simulation parameters" loaded={simulationParameters.length > 0}>
                            <div class="align h-center mb-5">
                                {#each simulationParameters as { label, value, id } (id)}
                                    <Textfield bind:value {label} />
                                {/each}
                            </div>

                            <div class="align h-center">
                                <CustomSelect
                                    options={$energyLevels.map((f) => f.label)}
                                    bind:value={$excitedFrom}
                                    label="excitedFrom"
                                />
                                <CustomSelect
                                    options={$energyLevels.map((f) => f.label)}
                                    bind:value={$excitedTo}
                                    label="excitedTo"
                                />
                                <Textfield value={$transitionFrequency.toFixed(3)} label="Frequency ({$energyUnit})" />
                            </div>
                        </CustomPanel>

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

                        <CustomPanel label="Lorrentz lineshape" loaded={powerBroadening.length > 0}>
                            {#each powerBroadening as { label, value, id } (id)}
                                <Textfield bind:value {label} />
                            {/each}
                            <Textfield bind:value={lorrentz} label="lorrentz - FWHM (MHz)" />
                            <Textfield value={voigtFWHM} label="Voigt - FWHM (MHz)" variant="outlined" />
                        </CustomPanel>

                        <EinsteinCoefficients {power} {gaussian} {trapArea} {lorrentz} />
                        <CollisionalCoefficients bind:numberDensity {collisionalTemp} {collisionalFilename} />
                        <AttachmentCoefficients bind:k3 bind:kCID bind:numberDensity bind:attachmentCoefficients />
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
        <ROSAA_Footer bind:showreport bind:statusReport bind:progress bind:simulationMethod {simulation} />
    </svelte:fragment>
</LayoutDiv>
