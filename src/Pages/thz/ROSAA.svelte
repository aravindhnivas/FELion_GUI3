
<script>
    import {mainPreModal} from "../../svelteWritable";
    // import { createEventDispatcher } from 'svelte';
    import {browse} from "../../components/Layout.svelte";
    import Textfield from '@smui/textfield';
    import {fade} from "svelte/transition";
    import SeparateWindow from '../../components/SeparateWindow.svelte';

    import CustomCheckbox from "../../components/CustomCheckbox.svelte";
    import CustomSelect from "../../components/CustomSelect.svelte";
    import BoltzmanDistribution from "./windows/BoltzmanDistribution.svelte";

    import { parse as Yml } from 'yaml';
    import EinsteinCoefficients from "./components/EinsteinCoefficients.svelte";
    import CollisionalCoefficients from "./components/CollisionalCoefficients.svelte";

    import AttachmentCoefficients from "./components/AttachmentCoefficients.svelte";


    import {PlanksConstant, SpeedOfLight, boltzmanConstant, DebyeToCm, VaccumPermitivity, amuToKG} from "./functions/constants";
    import {findAndGetValue} from "./functions/misc";
    //////////////////////////////////////////////////////////////////////////////////////////////////////////

    
    export let active=false;
    // const dispatch = createEventDispatcher();

    let electronSpin=false, zeemanSplit= false;
    let collisionalRateType = "excitation"
    // let trapTemp = 5.7
    
    let [mainParameters, simulationParameters, dopplerLineshape, powerBroadening] = Array(4).fill([])
    let attachmentCoefficients=[], k3={constant:[], rate:[]}, kCID={constant:[], rate:[]};
    $: deexcitation = collisionalRateType==="deexcitation";
    let py, pyProcesses=[], running = false;

    const pyEventHandle = (e) => {
        statusReport = ""
    
        const events = e.detail

        py = events.py;
        console.log(py);

        pyProcesses = [...pyProcesses, py]
    }

    let statusReport = "";

    let showreport = false

    const pyEventDataReceivedHandle = (e) => {
        let dataReceived = e.detail.dataReceived

        statusReport += `${dataReceived}\n`
    }

    const pyEventClosedHandle = (e) => {
        running=false; 
        pyProcesses = _.difference(pyProcesses, [e.detail.py]);
        window.createToast("Terminated", "danger")
        statusReport += "\n######## TERMINATED ########"
    }

    const pyKillProcess = () => {
        const lastInvokedPyProcess = _.last(pyProcesses);

        if(lastInvokedPyProcess) {

            lastInvokedPyProcess.kill(); pyProcesses.pop()
        }
    }

    let collisionalRates = []

    let collisionalRateConstants = []

    let einsteinB_rateComputed=false;
    const simulation = (e) => {
        if(!fs.existsSync(currentLocation)) return window.createToast("Location doesn't exist", "danger");
        if(!configLoaded) return window.createToast("Config file not loaded", "danger");
        if(!transitionFrequency) return window.createToast("Transition frequency is not defined", "danger");
        if(!einsteinB_rateComputed) return window.createToast("Compute einsteinB rate constants", "danger");
        if(includeCollision) {
            collisionalRateConstants = [...collisionalCoefficient, ...collisionalCoefficient_balance]
            if(collisionalRateConstants.length<1) return window.createToast("Compute collisional rate constants", "danger")
        
        }

        if(includeAttachmentRate){
            if(k3.constant.length<1) return window.createToast("Compute attachment rate constants", "danger")
        }
        
        const collisional_rates = {}
        collisionalRateConstants.forEach(f=>collisional_rates[f.label] = f.value)

        const main_parameters = {}
        mainParameters.forEach(f=>main_parameters[f.label]=f.value)

        const simulation_parameters = {}
        simulationParameters.forEach(f=>simulation_parameters[f.label]=f.value)

        const lineshape_conditions = {}
        dopplerLineshape.forEach(f=>lineshape_conditions[f.label]=f.value)

        const power_broadening = {}
        powerBroadening.forEach(f=>power_broadening[f.label]=f.value)

        const einstein_coefficient = {A:{}, B:{}};
        einsteinCoefficientA.forEach(f=>einstein_coefficient.A[f.label]=f.value)
        einsteinCoefficientB.forEach(f=>einstein_coefficient.B[f.label]=f.value)

        const attachment_rate_coefficients = {rateConstants:{k3:k3.constant.map(rate=>rate.value), kCID:kCID.constant.map(rate=>rate.value)}}
        
        attachmentCoefficients.forEach(f=>attachment_rate_coefficients[f.label]=f.value)
        const energy_levels = {}
        energyLevels.forEach(f=>energy_levels[f.label]=f.value)
        const conditions = { 
            trapTemp, variable, variableRange, numberOfLevels, includeCollision, includeAttachmentRate, includeSpontaneousEmission, writefile, savefilename, currentLocation,  deexcitation, collisional_rates, main_parameters, simulation_parameters, einstein_coefficient, energy_levels, energyUnit, power_broadening, lineshape_conditions, attachment_rate_coefficients, electronSpin, zeemanSplit, excitedFrom, excitedTo, numberDensity
        
        }
        
        const pyfile = "ROSAA/ROSAA_simulation.py"
        
        const args = [JSON.stringify(conditions)]
        
        computePy_func({e, pyfile, args, general:true}).catch(err=>{$mainPreModal.modalContent = err.stack;  $mainPreModal.open = true})
        running=true
    }
    let currentLocation = fs.existsSync(db.get("thz_modal_location")) ? db.get("thz_modal_location") : "";



    let savefilename = ""

    $: if(currentLocation&&fs.existsSync(currentLocation)) {db.set("thz_modal_location", currentLocation)}
    async function browse_folder() {

        const result = await browse({dir:true})
        if (!result.canceled) { currentLocation = result.filePaths[0]; }
    }

    let writefile = true, includeCollision = true, includeSpontaneousEmission = true, includeAttachmentRate = true;

    let variable = "time", variableRange = "1e12, 1e16, 10";
    const variablesList = ["time", "He density(cm3)", "Power(W)"]

    let collisionalCoefficient=[], einsteinCoefficientA=[], einsteinCoefficientB=[];

    let energyUnit="cm-1", numberDensity = "2e14";
    let numberOfLevels = 3;
    let energyLevels = [];
    let boltzmanWindow = false;
    let energyFilename, collisionalFilename, einsteinFilename;
    $: boltzmanArgs = {energyLevels, trapTemp, electronSpin, zeemanSplit, energyUnit}

    let collisionalCoefficient_balance = [];
    let configFile = db.get("ROSAA_config_file") || ""
    let configLoaded = false;

    async function loadConfig() {
    
        try {
            if(fs.existsSync(configFile)) return setConfig();

            const congFilePath = await browse({dir:false, multiple:false})
            if (congFilePath.filePaths.length==0) return Promise.reject("No files selected");
            configFile = congFilePath.filePaths[0]
            db.set("ROSAA_config_file", configFile)
            setConfig()
        
        } catch (error) {$mainPreModal = {modalContent:error, open:true}}
    }

    const getYMLFileContents = (filename) => {
        if (fs.existsSync(filename)) {
            const fileContent = fs.readFileSync(filename, "utf-8")
            const YMLcontent = Yml(fileContent)
            return Promise.resolve(YMLcontent)
        } else return Promise.reject(filename + " file doesn't exist")
    }

    
    const setID = (obj) => {
        obj.id = window.getID();
        return obj
    }

    const correctObjValue = (obj) => {
        obj.value = obj.value.toExponential(3)
        return obj

    }

    let trapArea;

    // Transition freq.
    let excitedTo, excitedFrom;
    let transitionFrequency=0, transitionFrequencyInHz;

    // Doppler linewidth parameters
    let ionMass=14, RGmass=4, ionTemp=12, trapTemp=5, gaussian=0, collisionalTemp=0;
    let Cg=0; // doppler-broadening proportionality constant

    // Lorrentz linewidth parameters
    let lorrentz=0, power="2e-5", dipole=1
    let Cp=0; // power-broadening proportionality constant
    // $: console.log({Cg, Cp});
    $: {
    
        if(energyLevels.length>1) {
            const {value:lowerLevelEnergy} = _.find(energyLevels, (energy)=>energy.label==excitedFrom)
            const {value:upperLevelEnergy} = _.find(energyLevels, (energy)=>energy.label==excitedTo)
            transitionFrequency = upperLevelEnergy - lowerLevelEnergy;
            transitionFrequencyInHz = energyUnit=="cm-1" ? transitionFrequency*SpeedOfLight*1e2 : transitionFrequency*1e6;
            // console.log({transitionFrequency, transitionFrequencyInHz})
        }

        if(dopplerLineshape.length) {
            [ionMass, RGmass, ionTemp, trapTemp] = dopplerLineshape.map(f=>f.value);
            collisionalTemp = Number((RGmass*ionTemp + ionMass*trapTemp)/(ionMass+RGmass)).toFixed(1);
            const sqrtTerm = 8*boltzmanConstant*Math.log(2) / (ionMass*amuToKG*SpeedOfLight
            **2)
            Cg = transitionFrequencyInHz*Math.sqrt(sqrtTerm)
            gaussian = Number(Cg*Math.sqrt(ionTemp)*1e-6).toFixed(3)
        };
        if(powerBroadening.length) {
            [dipole, power] = powerBroadening.map(f=>f.value);
            trapArea = findAndGetValue(mainParameters, "trap_area (sq-meter)")

            Cp = (2*dipole*DebyeToCm/PlanksConstant) * Math.sqrt( 1 / (trapArea*SpeedOfLight*VaccumPermitivity) );

            lorrentz = Number(Cp*Math.sqrt(power)*1e-6).toFixed(3)

        };
    }

    async function setConfig() {

        try {

            const configFileLocation = window.path.dirname(configFile);
            const CONFIG = Yml(fs.readFileSync(configFile, "utf-8"));

            let attachmentRateConstants = {};
            ({mainParameters, simulationParameters, dopplerLineshape, powerBroadening, attachmentCoefficients, attachmentRateConstants} = CONFIG);
            mainParameters = mainParameters.map(setID);
            simulationParameters = simulationParameters.map(setID);
            dopplerLineshape = dopplerLineshape.map(setID);
            powerBroadening = powerBroadening.map(setID);

            attachmentCoefficients = attachmentCoefficients.map(setID);

            k3.constant = attachmentRateConstants.k3.map(setID).map(correctObjValue);
            kCID.constant = attachmentRateConstants.kCID.map(setID).map(correctObjValue);

            ({trapTemp, electronSpin, zeemanSplit, numberDensity} = CONFIG);

            ({savelocation:currentLocation, savefilename}=CONFIG.saveFile);
            ({energy:energyFilename, collision:collisionalFilename, einsteinA:einsteinFilename} = CONFIG.filenames);

            energyFilename = window.path.join(configFileLocation, energyFilename);
            collisionalFilename = window.path.join(configFileLocation, collisionalFilename);
            einsteinFilename = window.path.join(configFileLocation, einsteinFilename);

            ({levels:energyLevels, unit:energyUnit} = await getYMLFileContents(energyFilename));
            
            energyLevels = energyLevels.map(setID);
            numberOfLevels = energyLevels.length;
            
            // ({rateConstants:collisionalCoefficient, type:collisionalRateType} = await getYMLFileContents(collisionalFilename));
            // collisionalCoefficient = collisionalCoefficient.map(setID).map(correctObjValue);

            ({rateConstants:einsteinCoefficientA} = await getYMLFileContents(einsteinFilename));
            einsteinCoefficientA = einsteinCoefficientA.map(setID).map(correctObjValue);
            console.log(energyLevels, collisionalCoefficient, einsteinCoefficientA);
            window.createToast("CONFIG loaded");
            configLoaded = true;

        } catch (error) {$mainPreModal = {modalContent:error, open:true}}
    }

</script>

<style lang="scss">
    .locationColumn {

        display: grid;
        grid-auto-flow: column;
        grid-gap: 1em;
        grid-template-columns: 1fr 4fr 2fr;

        .button {
            margin:0;
            align-self: center;
        }

    }

    hr {background-color: #fafafa; margin: 0;}
    .writefileCheck {

        display: grid;
        grid-auto-flow: column;
        border: solid 1px white;
        border-radius: 20px;
    }

    .variableColumn {

        display: grid;

        .subtitle {margin: 0;}
        
        .variableColumn__dropdown {
            display: flex;
            gap: 1em;

            place-items: baseline;
        }
    }
    .main_container__div {
        display: grid;
        grid-row-gap: 1em;
        padding: 1em;
        .subtitle {margin:0;}

    }
    // :global(.content__div label) {flex-basis: 30%;}
    .sub_container__div {
        display: grid;

        grid-row-gap: 1em;
        .subtitle {place-self:center;}
        .content__div {

            max-height: 30rem;
            overflow-y: auto;
            display: flex;
            flex-wrap: wrap;
            justify-self: center; // grow from center (width is auto adjusted)

            gap: 1em;
            justify-content: center; // align items center

        }
        .control__div {

            display: flex;
            align-items: baseline;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1em;
        }
    }

    .status_report__div {

        white-space: pre-wrap; 
        -webkit-user-select: text;
        padding:1em;
    }

</style>

{#if active}

    <BoltzmanDistribution {...boltzmanArgs} bind:active={boltzmanWindow} maximize={false}/>
    <SeparateWindow id="ROSAA__modal" title="ROSAA modal" bind:active>

        <svelte:fragment slot="header_content__slot" >
            <div class="locationColumn" >
                <button class="button is-link" id="thz_modal_filebrowser_btn" on:click={browse_folder}>Browse</button>
                <Textfield bind:value={currentLocation} label="Current location" />

                <Textfield bind:value={savefilename} label="savefilename" />
            </div>

            <div class="writefileCheck">
                <CustomCheckbox bind:selected={writefile} label="writefile" />
                <CustomCheckbox bind:selected={includeCollision} label="includeCollision" />
                <CustomCheckbox bind:selected={includeAttachmentRate} label="includeAttachmentRate" />

                <CustomCheckbox bind:selected={includeSpontaneousEmission} label="includeSpontaneousEmission" />
                <CustomCheckbox bind:selected={electronSpin} label="Electron Spin" />
                <CustomCheckbox bind:selected={zeemanSplit} label="Zeeman" />
            </div>

            <div class="variableColumn">
                <div class="subtitle">Simulate signal(%) as a function of {variable}</div>
                <div class="variableColumn__dropdown">
                    
                    <CustomSelect options={variablesList} bind:picked={variable} />
                    {#if variable !== "time"}
                        <Textfield bind:value={variableRange} label="Range (min, max, totalsteps)" style="width: auto;"/>
                    {/if}
                    <button class="button is-link" on:click={loadConfig}>Load config</button>
                    <button class="button is-link" on:click={()=>{configFile=""; window.createToast("Config file cleared", "warning")}}>Reset Config</button>

                </div>

            </div>
        </svelte:fragment>

        <svelte:fragment slot="main_content__slot">
            {#if showreport}
                <div class="content status_report__div" ><hr>{statusReport || "Status report"}<hr></div>
            {:else}

                <!-- Main Parameters -->

                <div class="main_container__div" >
                    <div class="sub_container__div box">

                        <div class="subtitle">Main Parameters</div>
                        <div class="content__div ">
                            {#each mainParameters as {label, value, id}(id)}
                                <Textfield bind:value {label}/>
                            {/each}
                        </div>
                    </div>

                    <!-- Energy levels -->

                    <div class="sub_container__div box" >
                        <div class="subtitle">Energy levels</div>
                        <div class="control__div ">

                            <Textfield bind:value={numberOfLevels} label="numberOfLevels (J levels)" input$step={1} input$min={0} input$type={"number"} />
                            <CustomSelect options={["MHz", "cm-1"]} bind:picked={energyUnit} />
                            <button class="button is-link " on:click={()=>boltzmanWindow=true}>Show Boltzman distribution</button>
                        </div>

                        <div class="content__div ">
                            {#each energyLevels as {label, value, id}(id)}
                                <Textfield bind:value {label} />
                            {/each}
                        </div>
                    </div>

                    <!-- Simulation parameters -->

                    <div class="sub_container__div box">
                        <div class="subtitle">Simulation parameters</div>
                        <div class="content__div ">

                            {#each simulationParameters as {label, value, id}(id)}
                                <Textfield bind:value {label} />
                            {/each}
                            <hr> <div class="subtitle" style="width: 100%; display:grid; place-items: center;">Transition levels</div> <hr>

                            <div class="align h-center">
                                <CustomSelect options={["", ...energyLevels.map(f=>f.label)]} bind:picked={excitedFrom} label="excitedFrom" style="min-width: 7em;"/>
                                <CustomSelect options={["", ...energyLevels.map(f=>f.label)]} bind:picked={excitedTo} label="excitedTo" style="min-width: 7em;"/>

                                <Textfield bind:value={transitionFrequency} label="transitionFrequency ({energyUnit})" />
                            </div>
                        </div>
                    </div>

                    <!-- Doppler lineshape -->

                    <div class="sub_container__div box">

                        <div class="subtitle">Doppler lineshape</div>
                        <div class="content__div ">
                            {#each dopplerLineshape as {label, value, type, step, id}(id)}
                                <Textfield bind:value {label} input$type={type} input$step={step}/>
                            {/each}

                            <Textfield bind:value={collisionalTemp} label="collisionalTemp(K)" disabled />
                            <Textfield bind:value={gaussian} label="gaussian(MHz)" disabled />
                        </div>
                    </div>
                    
                    
                    <!-- Lorrentz lineshape -->

                    <div class="sub_container__div box">
                        <div class="subtitle">Lorrentz lineshape</div>
                        <div class="content__div ">
                            {#each powerBroadening as {label, value, id}(id)}
                                <Textfield bind:value {label} />
                            {/each}
                            <Textfield bind:value={lorrentz} label="lorrentz(MHz)" disabled />
                        </div>

                    </div>

                    <EinsteinCoefficients bind:einsteinCoefficientA bind:einsteinCoefficientB bind:einsteinB_rateComputed {energyLevels} {electronSpin} {zeemanSplit} {energyUnit} {gaussian} {trapArea} {lorrentz} {power} />

                    {#if includeCollision}
                        <CollisionalCoefficients bind:collisionalCoefficient bind:collisionalCoefficient_balance bind:collisionalRateType bind:collisionalRates bind:numberDensity {...{energyLevels, electronSpin, zeemanSplit, energyUnit, collisionalFilename, collisionalTemp}}  />
                        
                    {/if}
                    
                    {#if includeAttachmentRate}
                        <AttachmentCoefficients bind:attachmentCoefficients bind:k3 bind:kCID bind:numberDensity />
                    {/if}
                    
                </div>

            {/if}

        </svelte:fragment>

        <svelte:fragment slot="footer_content__slot">
        
            <div class="align">
                {#if pyProcesses.length>0}
                    <div >Running: {pyProcesses.length} {pyProcesses.length>1 ? "simulations" : "simulation"}</div>
                {/if}
                
                {#if pyProcesses.length>0}
                    <button transition:fade class="button is-danger" on:click="{pyKillProcess}" >Stop</button>
                {/if}
                <button  class="button is-link" on:click="{(e)=>{showreport = !showreport}}" >{showreport ? "Go Back" : "Status report"}</button>
                <button  class="button is-link" on:click="{simulation}" on:pyEvent={pyEventHandle} on:pyEventClosed="{pyEventClosedHandle}" on:pyEventData={pyEventDataReceivedHandle}>Submit</button>
            </div>
        </svelte:fragment>
    
    </SeparateWindow>

{/if}