
<script>
    import { createEventDispatcher } from 'svelte';
    import {browse} from "../../components/Layout.svelte";
    import Textfield from '@smui/textfield';
    // import Modal from '../../components/Modal.svelte';
    import SeparateWindow from '../../components/SeparateWindow.svelte';

    import CustomCheckbox from "../../components/CustomCheckbox.svelte";
    import CustomSelect from "../../components/CustomSelect.svelte";
    export let active=false;
    const dispatch = createEventDispatcher();

    let mainParameters = [
    
        {label:"molecule", value:"CD", id:window.getID()},
        
        {label:"tagging partner", value:"He", id:window.getID()},
        
        {label:"freq", value:"453_521_850_000", id:window.getID()},
        {label:"trap_area", value:"5e-5", id:window.getID()},
        {label:"Energy", value:"0, 15.127861, 45.373851", id:window.getID()},
    ]

    let simulationParameters = [

        {label:"totalIonCounts", value:1000, id:window.getID()},
        
        {label:"Simulation time(ms)", value:600, id:window.getID()},
        {label:"Total steps", value:1000, id:window.getID()},
        {label:"excitedTo", value:1, id:window.getID()},
        {label:"excitedFrom", value:0, id:window.getID()},
    ]

    let dopplerLineshape = [
        
        {label:"IonMass(amu)", value:14, id:window.getID()},
        
        {label:"IonTemperature(K)", value:12, id:window.getID()},
    
    ]

    let powerBroadening = [

    
        {label:"cp", value:"4.9e7", id:window.getID()},
        {label:"dipoleMoment(D)", value:0, id:window.getID()},
        {label:"power(W)", value:"2e-5", id:window.getID()},
    ]

    let einsteinCoefficient = [ 
        {label:"A_10", value:"6.24e-4", id:window.getID()}
    ]

    let trapTemp = 5.7
    let rateCoefficients = [

        {label:"totalAttachmentLevels", value:2, id:window.getID()},
        {label:"branching-ratio", value:0.5, id:window.getID()},
        {label:"a", value:0.5, id:window.getID()},
        {label:"He density(cm3)", value:"2e14", id:window.getID()},
        {label:"k3", value:"9.6e-31, 2.9e-30", id:window.getID()},
        
        {label:"kCID", value:"6.7e-16, 1.9e-15", id:window.getID()},
    ]

    let collisionalRateType = "deexcitation"

    $: deexcitation = collisionalRateType==="deexcitation";
    let numberOfLevels = 3;

    $: collisionalCoefficient = _.range(1, numberOfLevels)
                                    .map(j=> _.range(j)
                                        .map(jj=> deexcitation ? {label:`q_${j}${jj}`, value:0, id:window.getID()} : {label:`q_${jj}${j}`, value:0, id:window.getID()})
                                    )

    let py, running = false;

    const pyEventHandle = (e) => {

        statusReport = ""
        const events = e.detail
        py = events.py
    }

    let statusReport = "";
    $: showreport = false
    $: buttonName = showreport ? "Go Back" : "Status report"
    const pyEventDataReceivedHandle = (e) => {
        let dataReceived = e.detail.dataReceived
        statusReport += `${dataReceived}\n`
    }
    $: console.log(statusReport)

    const pyEventClosedHandle = (e) => {
        running=false;
        window.createToast("Terminated", "danger")
        statusReport += "\n######## TERMINATED ########"
    }

    const simulation = (e) => {
        const collisionalRates = window._.flatten(collisionalCoefficient)

        const collisional_rates = {}
        collisionalRates.forEach(f=>collisional_rates[f.label] = parseFloat(document.querySelector(`#${f.label} input`).value) )

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
        
        const conditions = { trapTemp, variable, variableRange, numberOfLevels, includeCollision, includeAttachmentRate, includeSpontaneousEmission, writefile, filename, currentLocation,  deexcitation, collisional_rates, main_parameters, simulation_parameters, einstein_coefficient, power_broadening, lineshape_conditions, rate_coefficients }
        dispatch('submit', { e, conditions })


        running=true

    }


    const style="width:12em; margin-bottom:1em;"
    let currentLocation = db.get("thz_modal_location") || db.get("thz_location") || ""
    let filename = `ROSAA_modal_${mainParameters[0].value}_${mainParameters[1].value}`
    $: if(currentLocation&&fs.existsSync(currentLocation)) {db.set("thz_modal_location")}

    function browse_folder() {

        browse({dir:true}).then(result=>{
            if (!result.canceled) { currentLocation = result.filePaths[0]; db.set("thz_modal_location", currentLocation)}

        })
    
    }

    let writefile = true, includeCollision = true, includeSpontaneousEmission = true, includeAttachmentRate = true;

    let variable = "time", variableRange = "1e12, 1e16, 10";
    const variablesList = ["time", "He density(cm3)", "Power(W)"]

</script>

<style lang="scss">

    .locationColumn {

        display: grid;

        grid-auto-flow: column;
        grid-gap: 1em;
        margin-bottom: 2em;
        grid-template-columns: 1fr 4fr 2fr;

        .button {
            margin:0;
            align-self: center;

        }

    }

    .writefileCheck {
        border: solid 1px white;
        display: grid;
        padding: 0.3em;
        margin: 1em;
        border-radius: 20px;
        float: right;
    
    }


    .variableColumn {

        display: grid;

        grid-template-columns: 1fr 2fr;

        grid-gap: 1em;
        margin: 2em 0;

    }

    .rates__div {
        display: grid;
        grid-gap: 1em;
        margin-bottom: 1em;

        .rates__mainContainer {
            max-height: 20rem;
            overflow: auto;
        }

    }

    // #ROSAA__modal {
    //     .subtitle {margin-bottom: 0}
    // }
    
    .attachmentDissociationRate__div {
        .rates__mainContainer {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(12em,1fr));
            grid-gap: 1em;
        
        }
    }

    .hide {display: none}

</style>


{#if active}
    <SeparateWindow id="ROSAA__modal" title="ROSAA modal" bind:active >

        <svelte:fragment slot="content" >

            <div class="content" class:hide={!showreport} style="white-space: pre-wrap; user">{statusReport}</div>

            <div class:hide={showreport}>
            
                <div class="locationColumn" >
                    <button class="button is-link" id="thz_modal_filebrowser_btn" on:click={browse_folder}>Browse</button>

                    <Textfield bind:value={currentLocation} label="Current location" />
                    <Textfield bind:value={filename} label="filename" />
                </div>

                <div class="writefileCheck">
                    <CustomCheckbox bind:selected={writefile} label="writefile" />
                </div>

                <div class="writefileCheck">
                    <CustomCheckbox bind:selected={includeCollision} label="includeCollision" />
                    <CustomCheckbox bind:selected={includeAttachmentRate} label="includeAttachmentRate" />
                    <CustomCheckbox bind:selected={includeSpontaneousEmission} label="includeSpontaneousEmission" />
                </div>


                <div class="subtitle">Simulate signal(%) as a function of "{variable}"</div>
                <div class="variableColumn">

                    <CustomSelect options={variablesList} bind:picked={variable} />
                    {#if variable !== "time"}
                        <Textfield bind:value={variableRange} label="Range (min, max, totalsteps)" />
                    {/if}
                </div>


                <div class="subtitle">Main Parameters</div>

                {#each mainParameters as {label, value, id}(id)}

                    <Textfield {style} bind:value {label}/>
                {/each}

                <div class="subtitle">Simulation parameters</div>
                {#each simulationParameters as {label, value, id}(id)}
                    <Textfield {style} bind:value {label}/>
                {/each}

                <Textfield {style} bind:value={numberOfLevels} label="numberOfLevel (J levels)"/>

                <div class="subtitle">Doppler lineshape</div>
                {#each dopplerLineshape as {label, value, id}(id)}
                    <Textfield {style} bind:value {label}/>
                {/each}

                <div class="subtitle">Lorrentz lineshape</div>
                {#each powerBroadening as {label, value, id}(id)}
                    <Textfield {style} bind:value {label}/>
                {/each}

                <div class="rates__div einsteinRate__div">
                    <div class="subtitle">Einstein Co-efficients</div>
                    <div class="rates__mainContainer">
                        {#each einsteinCoefficient as {label, value, id}(id)}
                            <Textfield style="width:12em;" bind:value {label}/>
                        {/each}
                    </div>
                </div>


                {#if includeCollision}

                    <div class="rates__div collisionalRate__div">

                        <div class="subtitle">Collisional rate constants</div>
                        <CustomSelect style="width: 12em;" options={["deexcitation", "excitation"]} bind:picked={collisionalRateType} />
                        <div class="rates__mainContainer">
                            <Textfield style="width:12em;" bind:value={trapTemp} label="trapTemp(K)"/>
                            {#each collisionalCoefficient as rateConstant}
                                <div class="">
                                    {#each rateConstant as {label, value, id}(id)}
                                        <Textfield style="width:12em;" {value} {label} id={label} />
                                    {/each}
                                </div>
                            {/each}
                        </div>

                    </div>

                {/if}
                

                <div class="rates__div attachmentDissociationRate__div">
                    <div class="subtitle">Rare-gas attachment (K3) and dissociation (kCID) constants</div>
                    <div class="rates__mainContainer">
                        {#each rateCoefficients as {label, value, id}(id)}
                            <Textfield bind:value {label}/>
                        {/each}
                    </div>
                </div>
            </div>
        </svelte:fragment>

        <svelte:fragment slot="footerbtn">

            <button  class="button is-danger" on:click="{()=>{py&&running? py.kill() : console.log('pyEvent is not available')}}" >Stop</button>

        
            <button  class="button is-link" on:click="{(e)=>{showreport = !showreport}}" >{buttonName}</button>
            <button  class="button is-link" class:is-loading={running} on:click="{simulation}" on:pyEvent={pyEventHandle} on:pyEventClosed="{pyEventClosedHandle}" on:pyEventData={pyEventDataReceivedHandle}>Submit</button>
        </svelte:fragment>

    </SeparateWindow>
{/if}