
<script>
    import {mainPreModal} from "../../svelteWritable";
    import { createEventDispatcher } from 'svelte';
    import {browse} from "../../components/Layout.svelte";
    import Textfield from '@smui/textfield';
    import {fade} from "svelte/transition";
    import SeparateWindow from '../../components/SeparateWindow.svelte';

    import CustomCheckbox from "../../components/CustomCheckbox.svelte";
    import CustomSelect from "../../components/CustomSelect.svelte";
    import EditCoefficients from './EditCoefficients.svelte';
    import balance_distribution from "./functions/balance_distribution";

    import BoltzmanDistribution from "./windows/BoltzmanDistribution.svelte";
    import CollisionalDistribution from "./windows/CollisionalDistribution.svelte";

    import {getEnergyLabels} from "./functions/level_labels";

    
    import {readFromFile} from "./functions/read_files";
    import { parse as Yml } from 'yaml';
    //////////////////////////////////////////////////////////////////////////////////////////////////////////

    export let active=false;
    
    const dispatch = createEventDispatcher();
    let electronSpin=false, zeemanSplit= false;
    let collisionalRateType = "excitation"
    let trapTemp = 5.7
    let excitedTo="excitedTo", excitedFrom="excitedFrom";
    let [mainParameters, simulationParameters, dopplerLineshape, powerBroadening, rateCoefficients] = Array(5).fill([])

    $: deexcitation = collisionalRateType==="deexcitation";
    let py, running = false;
    const pyEventHandle = (e) => {
        statusReport = ""
        const events = e.detail
        py = events.py
    }

    let statusReport = "";
    let showreport = false

    const pyEventDataReceivedHandle = (e) => {
        let dataReceived = e.detail.dataReceived

        statusReport += `${dataReceived}\n`
    }

    const pyEventClosedHandle = (e) => {
        running=false;
        window.createToast("Terminated", "danger")
        statusReport += "\n######## TERMINATED ########"
    }

    const simulation = (e) => {

        const collisional_rates = {}
        collisionalCoefficient.forEach(f=>collisional_rates[f.label] = f.value)

        const main_parameters = {}
        mainParameters.forEach(f=>main_parameters[f.label]=f.value)


        const simulation_parameters = {}

        simulationParameters.forEach(f=>simulation_parameters[f.label]=f.value)


        const lineshape_conditions = {}
        dopplerLineshape.forEach(f=>lineshape_conditions[f.label]=f.value)

        const power_broadening = {}
        powerBroadening.forEach(f=>power_broadening[f.label]=f.value)

        const einstein_coefficient = {}
        einsteinCoefficient.forEach(f=>einstein_coefficient[f.label]=f.value)

        const rate_coefficients = {}
        rateCoefficients.forEach(f=>rate_coefficients[f.label]=f.value)

        const energy_levels = {}
        energyLevels.forEach(f=>energy_levels[f.label]=f.value)
        
        const conditions = { 
            trapTemp, variable, variableRange, numberOfLevels, includeCollision, includeAttachmentRate, includeSpontaneousEmission, writefile, filename, currentLocation,  deexcitation, collisional_rates, main_parameters, simulation_parameters, einstein_coefficient, energy_levels, energyUnit, power_broadening, lineshape_conditions, rate_coefficients, electronSpin, zeemanSplit, excitedFrom, excitedTo
        
        }
        
        dispatch('submit', { e, conditions })
        running=true
    }

    let currentLocation = db.get("thz_modal_location") || db.get("thz_location") || "";
    let filename = ""
    $: if(currentLocation&&fs.existsSync(currentLocation)) {db.set("thz_modal_location", currentLocation)}

    async function browse_folder() {
        const result = await browse({dir:true})
        if (!result.canceled) { currentLocation = result.filePaths[0]; }
    }

    let writefile = true, includeCollision = true, includeSpontaneousEmission = true, includeAttachmentRate = true;
    let variable = "time", variableRange = "1e12, 1e16, 10";
    const variablesList = ["time", "He density(cm3)", "Power(W)"]

    let collisionalCoefficient=[], einsteinCoefficient=[];

    function changeCollisionalRateType() {
        collisionalCoefficient = collisionalCoefficient.map(level=>{
            const level_arr = level.label.split(" --> ")

            const label = `${level_arr[1]} --> ${level_arr[0]}`
            return {label, value:level.value}

        })
    
    }

    let energyUnit="cm-1";
    let numberOfLevels = 3;
    let {energyLevels=[]} = getEnergyLabels({numberOfLevels, electronSpin, zeemanSplit})
    let boltzmanWindow = false;
    let energyFilename, collisionalFilename, einsteinFilename;
    $: boltzmanArgs = {energyLevels, trapTemp, electronSpin, zeemanSplit, energyUnit}

    const compteCollisionalBalanceConstants = () => {

        const balanceArgs  = {energyLevels, trapTemp,  electronSpin, zeemanSplit, energyUnit}

        collisionalCoefficient_balance = collisionalCoefficient.map(coefficient=>{
            const {label, value} = coefficient

            const levelLabels = label.split(" --> ").map(f=>f.trim())
            let newLabel, newValue;
            if(deexcitation) {
                const [excitedLevel, groundLevel] = levelLabels
                newValue = value*balance_distribution({...balanceArgs, groundLevel, excitedLevel})

                newLabel = `${groundLevel} --> ${excitedLevel}`
            } else {

                const [groundLevel, excitedLevel] = levelLabels
                newValue = value*balance_distribution({...balanceArgs, groundLevel:excitedLevel, excitedLevel:groundLevel})
                newLabel = `${excitedLevel} --> ${groundLevel}`
            }
            return {label:newLabel, value:newValue.toExponential(3), id:getID()}

        })
    }

    let collisionalWindow = false;
    let collisionalCoefficient_balance = [];
    $: collisionalRateConstants = [...collisionalCoefficient, ...collisionalCoefficient_balance]
    $: collisionalArgs = {collisionalRateConstants, energyLevels, electronSpin, zeemanSplit, energyUnit}
    
    let configFile = db.get("ROSAA_config_file") || ""

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

    async function setConfig() {
        try {

            const configFileLocation = window.path.dirname(configFile);
            
            const CONFIG = Yml(fs.readFileSync(configFile, "utf-8"));
            
            ({mainParameters, simulationParameters, dopplerLineshape, powerBroadening, rateCoefficients} = CONFIG);
            ({trapTemp, electronSpin, zeemanSplit, energyUnit, currentLocation, filename} = CONFIG);
            ({energyFilename, collisionalFilename, einsteinFilename} = CONFIG);

            energyFilename = window.path.join(configFileLocation, energyFilename);
            collisionalFilename = window.path.join(configFileLocation, collisionalFilename);
            einsteinFilename = window.path.join(configFileLocation, einsteinFilename);

            ({levels:energyLevels, unit:energyUnit} = await getYMLFileContents(energyFilename));
            numberOfLevels = energyLevels.length;
            ({rateConstants:collisionalCoefficient, type:collisionalRateType} = await getYMLFileContents(collisionalFilename));
            ({rateConstants:einsteinCoefficient} = await getYMLFileContents(einsteinFilename));
            window.createToast("CONFIG loaded");
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
    // .center {
    //     margin:auto;
    //     width:max-content;

    // }

</style>


{#if active}

    <BoltzmanDistribution {boltzmanArgs} bind:active={boltzmanWindow} />
    <CollisionalDistribution {...collisionalArgs} bind:active={collisionalWindow} />

    <SeparateWindow id="ROSAA__modal" title="ROSAA modal" bind:active >
        <svelte:fragment slot="header_content__slot" >
            <div class="locationColumn" >

                <button class="button is-link" id="thz_modal_filebrowser_btn" on:click={browse_folder}>Browse</button>
                <Textfield bind:value={currentLocation} label="Current location" />
                <Textfield bind:value={filename} label="filename" />
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
                        {#each mainParameters as {label, value}(label)}
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
                        {#each energyLevels as {label, value}(label)}
                            <Textfield bind:value {label} />
                        {/each}
                    </div>
                </div>

                {#if includeSpontaneousEmission}
                    <div class="sub_container__div box">
                        <div class="subtitle">Einstein Co-efficients</div>
                        
                        {#if einsteinCoefficient.length>0}
                            <div class="content__div ">
                                {#each einsteinCoefficient as {label, value}(label)}
                                    <Textfield bind:value {label} />
                                {/each}
                            </div>
                        {/if}

                    </div>
                {/if}

                {#if includeCollision}

                    <div class="sub_container__div box">
                        <div class="subtitle">Collisional rate constants</div>
                        <div class="control__div ">
                            <CustomSelect options={["deexcitation", "excitation", "both"]} bind:picked={collisionalRateType} on:change={changeCollisionalRateType}/>

                            <button class="button is-link " on:click={compteCollisionalBalanceConstants}>Compute balance rate</button>
                            <button class="button is-link " on:click={()=>collisionalWindow=true}>Compute Collisional Cooling</button>
                        </div>

                        {#if collisionalCoefficient.length>0}
                            <div class="content__div ">
                                {#each collisionalCoefficient as {label, value}(label)}
                                    <Textfield bind:value {label}/>
                                {/each}
                            </div>
                            {/if}

                        {#if collisionalCoefficient_balance.length>0}
                            <div class="content__div ">

                                <hr><hr>
                                {#each collisionalCoefficient_balance as {label, value}(label)}
                                    <Textfield bind:value {label}/>
                                {/each}
                            </div>
                        {/if}

                    </div>
                {/if}
                
                <!-- Simulation parameters -->

                <div class="sub_container__div box">
                    <div class="subtitle">Simulation parameters</div>
                    <div class="content__div ">

                        {#each simulationParameters as {label, value}(label)}
                            <Textfield bind:value {label} />
                        {/each}
                        <hr> <div class="subtitle" style="width: 100%; display:grid; place-items: center;">Transition levels</div> <hr>

                        <div style="display: flex; gap: 1em; place-content: center; width: 100%;">
                            <CustomSelect options={["excitedFrom", ...energyLevels.map(f=>f.label)]} 
                                bind:picked={excitedFrom} />
                            <CustomSelect options={["excitedTo", ...energyLevels.map(f=>f.label)]} 
                                bind:picked={excitedTo} />

                        </div>
                    </div>

                </div>

                <!-- Doppler lineshape -->
                <div class="sub_container__div box">
                    <div class="subtitle">Doppler lineshape</div>
                    <div class="content__div ">
                        <Textfield bind:value={trapTemp} label="trapTemp(K)"/>
                        {#each dopplerLineshape as {label, value, type, step}(label)}
                            <Textfield bind:value {label} input$type={type} input$step={step}/>
                        {/each}
                    </div>
                </div>
                
                <!-- Lorrentz lineshape -->
                <div class="sub_container__div box">
                    <div class="subtitle">Lorrentz lineshape</div>
                    <div class="content__div ">
                        {#each powerBroadening as {label, value}(label)}
                            <Textfield bind:value {label} />
                        {/each}
                    </div>
                </div>

                {#if includeAttachmentRate}
                    <div class="sub_container__div box">
                        <div class="subtitle">Rare-gas attachment (K3) and dissociation (kCID) constants</div>
                        <div class="content__div">
                            {#each rateCoefficients as {label, value}(label)}
                                <Textfield bind:value {label}  />
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>
            {/if}

        </svelte:fragment>

        <svelte:fragment slot="footer_content__slot">

            <div style="display: flex; gap: 1em; ">
                {#if running}
                    <button transition:fade class="button is-danger" on:click="{()=>{py ? py.kill() : console.log('pyEvent is not available')}}" >Stop</button>
                {/if}    
            
                <button  class="button is-link" on:click="{(e)=>{showreport = !showreport}}" >{showreport ? "Go Back" : "Status report"}</button>
                <button  class="button is-link" class:is-loading={running} on:click="{simulation}" on:pyEvent={pyEventHandle} on:pyEventClosed="{pyEventClosedHandle}" on:pyEventData={pyEventDataReceivedHandle}>Submit</button>
            </div>
        </svelte:fragment>
    
    </SeparateWindow>

{/if}