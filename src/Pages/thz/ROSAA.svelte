
<script>
    import { createEventDispatcher } from 'svelte';
    import {browse} from "../../components/Layout.svelte";
    import Textfield from '@smui/textfield';
    import {fade} from "svelte/transition";
    import SeparateWindow from '../../components/SeparateWindow.svelte';

    import CustomCheckbox from "../../components/CustomCheckbox.svelte";
    import CustomSelect from "../../components/CustomSelect.svelte";
    import EditCoefficients from './EditCoefficients.svelte';
    // import EinsteinACoefficients from './EinsteinACoefficients.svelte';

    export let active=false;
    const dispatch = createEventDispatcher();

    const mainParameters = [
    
        {label:"molecule", value:"CD", id:window.getID()},
        
        {label:"tagging partner", value:"He", id:window.getID()},
        
        {label:"freq", value:"453_521_850_000", id:window.getID()},
        {label:"trap_area", value:"5e-5", id:window.getID()},
        {label:"Energy", value:"0, 15.127861, 45.373851", id:window.getID()},
    ]

    const simulationParameters = [

        {label:"totalIonCounts", value:1000, id:window.getID()},
        
        {label:"Simulation time(ms)", value:600, id:window.getID()},
        {label:"Total steps", value:1000, id:window.getID()},
        {label:"excitedTo", value:1, id:window.getID()},
        {label:"excitedFrom", value:0, id:window.getID()},
    ]


    const dopplerLineshape = [

        {label:"IonMass(amu)", value:14, id:window.getID(), type:"number", step:1},
        
        {label:"IonTemperature(K)", value:12, id:window.getID(), type:"number", step:0.5},
    ]



    const powerBroadening = [

        {label:"cp", value:"4.9e7", id:window.getID()},
        {label:"dipoleMoment(D)", value:0, id:window.getID()},

        {label:"power(W)", value:"2e-5", id:window.getID()},
    ]


    // $: einsteinCoefficient = _.range(numberOfLevels).map(i=>{return {label:`A${i+1}${i}`, value:"0", id:window.getID()}})

    let trapTemp = 5.7
    const rateCoefficients = [

        {label:"totalAttachmentLevels", value:2, id:window.getID()},
        {label:"branching-ratio(kCID)", value:0.5, id:window.getID()},
        {label:"a(k31)", value:0.5, id:window.getID()},
        {label:"He density(cm3)", value:"2e14", id:window.getID()},
        {label:"k3", value:"9.6e-31, 2.9e-30", id:window.getID()},
        
        {label:"kCID", value:"6.7e-16, 1.9e-15", id:window.getID()},
    ]

    
    let electronSpin=false, zeemanSplit= false;
    let collisionalRateType = "deexcitation"

    $: deexcitation = collisionalRateType==="deexcitation";

    let numberOfLevels = 3;


    // $: collisionalCoefficient = _.range(1, numberOfLevels)
    //                                 .map(j=> _.range(j)
    //                                     .map(jj=> deexcitation ? {label:`q_${j}${jj}`, value:0, id:window.getID()} : {label:`q_${jj}${j}`, value:0, id:window.getID()})
    //                                 );

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
        const collisionalRates = window._.flatten(collisionalCoefficient)
        const collisional_rates = {}
        if (includeCollision) {
            collisionalRates.forEach(f=>collisional_rates[f.label] = parseFloat(document.querySelector(`#${f.label} input`).value) )
        }

        const main_parameters = {}
        mainParameters.forEach(f=>main_parameters[f.label]=f.value)

        const simulation_parameters = {}
        simulationParameters.forEach(f=>simulation_parameters[f.label]=f.value)

        const lineshape_conditions = {}
        dopplerLineshape.forEach(f=>lineshape_conditions[f.label]=f.value)

        const power_broadening = {}
        powerBroadening.forEach(f=>power_broadening[f.label]=f.value)

        // const einstein_coefficient = einsteinCoefficient.map(f=>f.value)
        const einstein_coefficient = {}
        einsteinCoefficient.forEach(f=>einstein_coefficient[f.label]=f.value)

        const rate_coefficients = {}
        rateCoefficients.forEach(f=>rate_coefficients[f.label]=f.value)
        
        const conditions = { trapTemp, variable, variableRange, numberOfLevels, includeCollision, includeAttachmentRate, includeSpontaneousEmission, writefile, filename, currentLocation,  deexcitation, collisional_rates, main_parameters, simulation_parameters, einstein_coefficient, power_broadening, lineshape_conditions, rate_coefficients, electronSpin, zeemanSplit }
        dispatch('submit', { e, conditions })
        running=true

    }



    let currentLocation = db.get("thz_modal_location") || db.get("thz_location") || "";

    let filename = `ROSAA_modal_${mainParameters[0].value}_${mainParameters[1].value}`;
    $: if(currentLocation&&fs.existsSync(currentLocation)) {db.set("thz_modal_location", currentLocation)}

    async function browse_folder() {
        const result = await browse({dir:true})
        if (!result.canceled) { currentLocation = result.filePaths[0]; }
    }

    let writefile = true, includeCollision = true, includeSpontaneousEmission = true, includeAttachmentRate = true;
    let variable = "time", variableRange = "1e12, 1e16, 10";
    const variablesList = ["time", "He density(cm3)", "Power(W)"]
    let editCollisionalCoefficients = false, editEinsteinCoefficients= false, collisionalCoefficient=[], einsteinCoefficient=[];
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

    hr {background-color: #fafafa;}
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
            display: grid;
            grid-auto-flow: column;
            grid-template-columns: auto 1fr;
            grid-column-gap: 1em;
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
            display: grid;
            grid-auto-flow: column;

            grid-gap: 1em;
            border: solid white 1px;
            padding: 1em;
            border-radius: 2em;
            place-content: center;
        }
    }

    .status_report__div {
        white-space: pre-wrap; 
        -webkit-user-select: text;
        padding:1em;
    }


    .center {
        margin:auto;
        width:max-content;
    }
</style>

<EditCoefficients title="Collisional rate constants" bind:active={editCollisionalCoefficients} bind:coefficients={collisionalCoefficient} />
<EditCoefficients title="Einstein Co-efficients" bind:active={editEinsteinCoefficients} bind:coefficients={einsteinCoefficient} />

{#if active}
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
                        <Textfield bind:value={variableRange} label="Range (min, max, totalsteps)" />
                    {/if}
                </div>
                
            </div>

        </svelte:fragment>

        <svelte:fragment slot="main_content__slot">

            {#if showreport}
                <div class="content status_report__div" ><hr>{statusReport || "Status report"}<hr></div>
            {:else}
            <div class="main_container__div" >
            
                <div class="sub_container__div">

                    <div class="subtitle">Main Parameters</div>
                    <div class="content__div">
                        {#each mainParameters as {label, value, id}(id)}
                            <Textfield bind:value {label}/>
                        {/each}
                    </div>
                </div>
                

                <div class="sub_container__div">
                    <div class="subtitle">Simulation parameters</div>
                    <div class="content__div">
                        {#each simulationParameters as {label, value, id}(id)}
                            <Textfield bind:value {label}/>
                        {/each}
                        <Textfield bind:value={numberOfLevels} label="numberOfLevels (J levels)"/>
                    </div>
                </div>
                

                <div class="sub_container__div">
                    <div class="subtitle">Doppler lineshape</div>
                    <div class="content__div">
                        {#each dopplerLineshape as {label, value, id, type, step}(id)}
                            <Textfield bind:value {label} input$type={type} input$step={step}/>
                        {/each}
                    </div>
                </div>

                
                <div class="sub_container__div">
                    <div class="subtitle">Lorrentz lineshape</div>
                    <div class="content__div">
                        {#each powerBroadening as {label, value, id}(id)}
                            <Textfield bind:value {label}/>
                        {/each}
                    </div>
                </div>
                
                {#if includeSpontaneousEmission}
                    <div class="sub_container__div">
                        <div class="subtitle">Einstein Co-efficients</div>
                        <button class="button is-link center" on:click={() => editEinsteinCoefficients=true}>Edit constats</button>

                        <div class="content__div">
                            {#each einsteinCoefficient as {label, value, id}(id)}
                                <Textfield {value} {label}/>
                            {/each}
                        </div>
                    </div>
                {/if}
                

                {#if includeCollision}

                    <div class="sub_container__div">
                        <div class="subtitle">Collisional rate constants</div>
                        <div class="content__div">
                            <CustomSelect options={["deexcitation", "excitation"]} bind:picked={collisionalRateType} />
                            <Textfield bind:value={trapTemp} label="trapTemp(K)"/>

                            <button class="button is-link" on:click={() => editCollisionalCoefficients=true}>Edit constats</button>
                        </div>

                        {#each collisionalCoefficient as {label, value, id}(id)}
                            <div class="content__div">
                                <Textfield  {value} {label} id={label} />
                            </div>
                        {/each}
                        
                    </div>

                {/if}

                
                {#if includeAttachmentRate}
                    
                    <div class="sub_container__div">

                        <div class="subtitle">Rare-gas attachment (K3) and dissociation (kCID) constants</div>

                        <div class="content__div">
                            {#each rateCoefficients as {label, value, id}(id)}

                                <Textfield bind:value {label} />
                            {/each}
                        </div>

                    </div>
                {/if}
            </div>

            {/if}
        </svelte:fragment>

        <svelte:fragment slot="footer_content__slot">

            {#if running}
                <button transition:fade class="button is-danger" on:click="{()=>{py ? py.kill() : console.log('pyEvent is not available')}}" >Stop</button>
            {/if}    
        
            <button  class="button is-link" on:click="{(e)=>{showreport = !showreport}}" >{showreport ? "Go Back" : "Status report"}</button>

            <button  class="button is-link" class:is-loading={running} on:click="{simulation}" on:pyEvent={pyEventHandle} on:pyEventClosed="{pyEventClosedHandle}" on:pyEventData={pyEventDataReceivedHandle}>Submit</button>
        </svelte:fragment>

    </SeparateWindow>

{/if}