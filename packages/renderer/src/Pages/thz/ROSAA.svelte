<script>

    import {fade}                   from "svelte/transition";
    import Textfield                from '@smui/textfield';
    import { parse as Yml }         from 'yaml';
    import {find}                   from "lodash-es"

    import {browse}                 from "$components/Layout.svelte";
    import CustomSelect             from "$components/CustomSelect.svelte";
    import SeparateWindow           from '$components/SeparateWindow.svelte';
    import CustomCheckbox           from "$components/CustomCheckbox.svelte";
    import PyButton                 from "$components/PyButton.svelte"
    
    import BoltzmanDistribution     from "./windows/BoltzmanDistribution.svelte";

    import EinsteinCoefficients     from "./components/EinsteinCoefficients.svelte";
    import CollisionalCoefficients  from "./components/CollisionalCoefficients.svelte";
    import AttachmentCoefficients   from "./components/AttachmentCoefficients.svelte";

    import {
        amuToKG,
        DebyeToCm,
        SpeedOfLight,
        PlanksConstant,
        boltzmanConstant,
        VaccumPermitivity
    }                               from "./functions/constants";
    
    import {findAndGetValue}        from "./functions/misc";
    import computePy_func           from "$src/Pages/general/computePy"

    //////////////////////////////////////////////////////////////////////////////////////////////////////////

    export let active = false;

    //////////////////////////////////////////////////////////////////////////////////////////////////////////

    let electronSpin        = false
    let zeemanSplit         = false;
    
    let [mainParameters, simulationParameters, dopplerLineshape, powerBroadening] = Array(4).fill([])

    let k3 = {constant:[], rate:[]}
    let kCID = {constant:[], rate:[]};
    let attachmentCoefficients=[]

    let collisionalRateType = "excitation"
    $: deexcitation = collisionalRateType==="deexcitation";

    let showreport = false

    let pyProcesses = [];
    let statusReport = "";

    let collisionalRates = []
    let collisionalRateConstants = []
    let einsteinB_rateComputed = false;

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
            trapTemp, variable, variableRange, numberOfLevels, includeCollision, includeAttachmentRate, 
            includeSpontaneousEmission, writefile, savefilename, currentLocation,  deexcitation, 
            collisional_rates, main_parameters, simulation_parameters, einstein_coefficient, 
            energy_levels, energyUnit, power_broadening, lineshape_conditions, attachment_rate_coefficients, 
            electronSpin, zeemanSplit, excitedFrom, excitedTo, numberDensity, collisionalTemp
        
        }
        
        const pyfile = "ROSAA_simulation"
        const args = [JSON.stringify(conditions)]
        
        computePy_func({e, pyfile, args, general:true})
    }
    let currentLocation = fs.existsSync(db.get("thz_modal_location")) ? db.get("thz_modal_location") : "";

    let savefilename = ""
    $: if(fs.existsSync(currentLocation)) {db.set("thz_modal_location", currentLocation)}

    async function browse_folder() {
        const result = await browse()
        if(!result) return
        currentLocation = result
    }
    
    let writefile = true
    let includeCollision = true
    let includeAttachmentRate = true;
    let includeSpontaneousEmission = true

    let variable = "time"
    let variableRange = "1e12, 1e16, 10";
    
    const variablesList = ["time", "He density(cm3)", "Power(W)"]
    
    let einsteinCoefficientA=[]
    let einsteinCoefficientB=[];
    let collisionalCoefficient=[]

    let energyUnit="cm-1"
    let energyLevels = [];
    let numberOfLevels = 3;
    let numberDensity = "2e14";

    let energyFilename
    let einsteinFilename;
    let collisionalFilename

    let configFile = db.get("ROSAA_config_file") || ""
    $: boltzmanArgs = {energyLevels, trapTemp, electronSpin, zeemanSplit, energyUnit}

    let configLoaded    = false;
    let collisionalCoefficient_balance = [];

    async function loadConfig() {
        
        try {
            
            if(fs.existsSync(configFile)) return setConfig();
            const congFilePath = await browse({dir:false, multiple:false})
            if (!congFilePath) return window.createToast("No files selected", "danger");
            configFile = congFilePath[0]
            db.set("ROSAA_config_file", configFile)
            setConfig()
        } catch (error) {window.handleError(error)}
    }

    const getYMLFileContents = (filename) => {
        if (fs.existsSync(filename)) {
            const fileContent   = fs.readFileSync(filename)
            const YMLcontent    = Yml(fileContent)
            return Promise.resolve(YMLcontent)

        } else return Promise.reject(filename + " file doesn't exist")
    }
    
    const setID = obj => ({...obj, id:getID()})
    const correctObjValue = obj =>({...obj, value: obj.value.toExponential(3)})

    let trapArea;
    let excitedTo=""
    let excitedFrom="";
    let transitionFrequency=0
    let transitionFrequencyInHz;

    // Doppler linewidth parameters
    let ionMass=14
    let RGmass=4
    let ionTemp=12
    let trapTemp=5
    let gaussian=0
    let collisionalTemp=0;
    let Cg=0; // doppler-broadening proportionality constant

    // Lorrentz linewidth parameters
    let power="2e-5"
    let dipole=1
    let lorrentz=0
    let Cp=0; // power-broadening proportionality constant

    const updateEnergyLevels = () => {
        console.log("energyLevels updated")

        const {value:lowerLevelEnergy}  = find(energyLevels, (energy)=>energy.label==excitedFrom) || 0
        const {value:upperLevelEnergy}  = find(energyLevels, (energy)=>energy.label==excitedTo) || 0
        transitionFrequency             = upperLevelEnergy - lowerLevelEnergy;
        if(energyUnit=="cm-1" ) { transitionFrequencyInHz     = transitionFrequency*SpeedOfLight*1e2 } 
        else { transitionFrequencyInHz     = transitionFrequency*1e6 }
        updateDoppler()
    }
    

    const updateDoppler = () => {

        console.log("Changing doppler parameters");
        [ionMass, RGmass, ionTemp, trapTemp] = dopplerLineshape.map(f=>f.value);
        collisionalTemp = Number((RGmass*ionTemp + ionMass*trapTemp)/(ionMass+RGmass)).toFixed(1);
        const sqrtTerm  = 8*boltzmanConstant*Math.log(2) / (ionMass*amuToKG*SpeedOfLight**2)
        Cg          = transitionFrequencyInHz*Math.sqrt(sqrtTerm)
        gaussian    = Number(Cg*Math.sqrt(ionTemp)*1e-6).toFixed(3)
    
    }

    const updatePower = () => {
    
        [dipole, power] = powerBroadening.map(f=>f.value);
        trapArea        = findAndGetValue(mainParameters, "trap_area (sq-meter)")
        Cp = (2*dipole*DebyeToCm/PlanksConstant) * Math.sqrt( 1 / (trapArea*SpeedOfLight*VaccumPermitivity) );
        lorrentz = Number(Cp*Math.sqrt(power)*1e-6).toFixed(3)
    }

    $: {
        if(energyLevels.length>1) { updateEnergyLevels() }
        if(dopplerLineshape.length) { updateDoppler() }
        if(powerBroadening.length) { updatePower() }
    }

    async function setConfig() {

        try {

            const configFileLocation = dirname(configFile);
            const CONFIG = Yml(fs.readFileSync(configFile));
            
            console.table(CONFIG)

            let attachmentRateConstants = {};
            
            ({
                mainParameters,
                powerBroadening,
                dopplerLineshape,
                simulationParameters,
                attachmentCoefficients,
                attachmentRateConstants
            } = CONFIG);
            
            mainParameters          = mainParameters.map(setID);
            powerBroadening         = powerBroadening.map(setID);
            dopplerLineshape        = dopplerLineshape.map(setID);
            simulationParameters    = simulationParameters.map(setID);

            attachmentCoefficients  = attachmentCoefficients.map(setID);
            k3.constant             = attachmentRateConstants.k3.map(setID).map(correctObjValue);
            kCID.constant           = attachmentRateConstants.kCID.map(setID).map(correctObjValue);
            
            ({
                trapTemp,
                zeemanSplit,
                electronSpin,
                numberDensity
            }                       = CONFIG);
            ({savefilename}         = CONFIG.saveFile);

            const {savelocation}    = CONFIG.saveFile;
            if(fs.existsSync(savelocation)) {currentLocation = savelocation};

            ({
                energy:energyFilename,
                einsteinA:einsteinFilename,
                collision:collisionalFilename
            }                           = CONFIG.filenames);

            energyFilename      = window.pathJoin(configFileLocation, energyFilename);
            einsteinFilename    = window.pathJoin(configFileLocation, einsteinFilename);
            collisionalFilename = window.pathJoin(configFileLocation, collisionalFilename);

            ({levels:energyLevels, unit:energyUnit} = await getYMLFileContents(energyFilename));

            energyLevels        = energyLevels.map(setID);
            numberOfLevels      = energyLevels.length;
            excitedFrom = energyLevels?.[0].label;
            excitedTo = energyLevels?.[1].label;

            ({rateConstants:einsteinCoefficientA}   = await getYMLFileContents(einsteinFilename));
            einsteinCoefficientA                    = einsteinCoefficientA.map(setID).map(correctObjValue);

            window.createToast("CONFIG loaded");
            console.log({energyLevels, collisionalCoefficient, einsteinCoefficientA});
            updatePower();
            updateDoppler();
            updateEnergyLevels();

            configLoaded = true;

        } catch (error) {window.handleError(error)}
    }

    let boltzmanWindow;
    let openBoltzmanWindow = false;

</script>

<BoltzmanDistribution {...boltzmanArgs}
    bind:active={openBoltzmanWindow} 
    bind:graphWindow={boltzmanWindow} 
/>
<SeparateWindow id="ROSAA__modal" title="ROSAA modal" bind:active>

    <svelte:fragment slot="header_content__slot" >
    
        <div class="locationColumn" >
            <button class="button is-link" id="thz_modal_filebrowser_btn" on:click={browse_folder}>Browse</button>
            <Textfield bind:value={currentLocation} label="Current location" />
            <Textfield bind:value={savefilename}    label="savefilename" />
        </div>

        <div class="writefileCheck">
            <CustomCheckbox bind:selected={writefile}                   label="writefile" />
            <CustomCheckbox bind:selected={includeCollision}            label="includeCollision" />
            <CustomCheckbox bind:selected={includeAttachmentRate}       label="includeAttachmentRate" />
            <CustomCheckbox bind:selected={includeSpontaneousEmission}  label="includeSpontaneousEmission" />
            <CustomCheckbox bind:selected={electronSpin}                label="Electron Spin" />
            <CustomCheckbox bind:selected={zeemanSplit}                 label="Zeeman" />
        </div>

        <div class="variableColumn">
            <div class="subtitle">Simulate signal(%) as a function of {variable}</div>
            <div class="variableColumn__dropdown">
                
                <CustomSelect options={variablesList} bind:picked={variable} />
            
                {#if variable !== "time"}
                    <Textfield bind:value={variableRange} style="width: auto;" label="Range (min, max, totalsteps)" />
                {/if}
            
                <button class="button is-link" on:click={loadConfig}>Load config</button>
                <button class="button is-link" 
                    on:click={()=>{configFile=""; window.createToast("Config file cleared", "warning")}}>
                    Reset Config
                </button>
            </div>

        </div>
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">
        <div class="content status_report__div" class:hide={!showreport} ><hr>{statusReport || "Status report"}<hr></div>

        <!-- Main Parameters -->
        <div class="main_container__div" class:hide={showreport}>
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

                    <Textfield bind:value={numberOfLevels} 
                        input$step={1}
                        input$min={0}
                        input$type={"number"} 
                        label="numberOfLevels (J levels)"
                    />
                    <CustomSelect options={["MHz", "cm-1"]} bind:picked={energyUnit} />

                    <button class="button is-link" 
                        on:click={()=>{openBoltzmanWindow=true; setTimeout(()=>boltzmanWindow?.focus(), 100); }}>
                        Show Boltzman distribution
                    </button>

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

                    <hr>
                        <div class="subtitle" style="width: 100%; display:grid; place-items: center;">
                            Transition levels
                        </div>
                    <hr>


                    <div class="align h-center">

                        <CustomSelect options={energyLevels.map(f=>f.label)} bind:picked={excitedFrom}
                            label="excitedFrom"
                            on:change={updateEnergyLevels}
                        />
                    
                        <CustomSelect options={energyLevels.map(f=>f.label)} bind:picked={excitedTo}
                            label="excitedTo"
                            on:change={updateEnergyLevels}
                        />
                    
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

                    <Textfield bind:value={collisionalTemp} label="collisionalTemp(K)" />
                    <Textfield bind:value={gaussian}        label="gaussian(MHz)"      />
                </div>
            </div>
            
            <!-- Lorrentz lineshape -->
            <div class="sub_container__div box">

                <div class="subtitle">Lorrentz lineshape</div>
                
                <div class="content__div ">
                
                    {#each powerBroadening as {label, value, id}(id)}
                        <Textfield bind:value {label} />
                    {/each}
                    <Textfield bind:value={lorrentz} label="lorrentz(MHz)" />
                
                </div>

            </div>
            
            <EinsteinCoefficients
                bind:einsteinCoefficientA
                bind:einsteinCoefficientB
                bind:einsteinB_rateComputed
                {power} 
                {gaussian}
                {trapArea}
                {lorrentz}
                {energyUnit}
                {zeemanSplit}
                {electronSpin}
                {energyLevels}
                />

            <!-- {#if includeCollision} -->
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
                />
                
            <!-- {/if} -->
            
            {#if includeAttachmentRate}
                <AttachmentCoefficients
                    bind:k3
                    bind:kCID
                    bind:numberDensity 
                    bind:attachmentCoefficients
                />
            {/if}
            
        </div>

    </svelte:fragment>

    <svelte:fragment slot="footer_content__slot">
        
        {#if pyProcesses.length>0}

            <div>Running: {pyProcesses.length} {pyProcesses.length>1 ? "simulations" : "simulation"}</div>
            <button transition:fade class="button is-danger" 
                on:click="{()=>{pyProcesses.at(-1).kill(); pyProcesses.pop()}}" >Stop</button>
        
        {/if}

        {#if showreport}
            <button  class="button is-warning" on:click="{()=>{statusReport = ""}}" >Clear</button>
        {/if}
        
        <button  class="button is-link" on:click="{()=>{showreport = !showreport}}">
            {showreport ? "Go Back" : "Status report"}

        </button>
    
        <PyButton on:click={simulation} bind:pyProcesses bind:stdOutput={statusReport} />

    </svelte:fragment>

</SeparateWindow>

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
        user-select: text;
        padding:1em;
    }
</style>
