
<script>
    import { createEventDispatcher } from 'svelte';
    import {browse} from "../../components/Layout.svelte";
    import Textfield from '@smui/textfield';
    import Modal from '../../components/Modal.svelte';
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
        {label:"numberOfLevel (J levels)", value:3, id:window.getID()},
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

    let einsteinCoefficient = [ {label:"SpontaneousEmission", value:"6.24e-4", id:window.getID()}]

    let collisionalCoefficient = [
        {label:"Collisional_q", value:"4.3242e-11, 3.4640e-11, 1.3013e-10", id:window.getID()},
        {label:"trapTemp(K)", value:5.7, id:window.getID()}
    ]

    let rateCoefficients = [
        {label:"branching-ratio", value:0.5, id:window.getID()},
        {label:"a", value:0.5, id:window.getID()},
        {label:"He density(cm3)", value:"2e14", id:window.getID()},
        {label:"k3", value:"9.6e-31, 2.9e-30", id:window.getID()},
        {label:"kCID", value:"6.7e-16, 1.9e-15", id:window.getID()},
    ]

    let py, running = false;

    const pyEventHandle = (e) => {

        statusReport = ""
        const events = e.detail
        py = events.py


    }

    let statusReport = "";
    $: reportToggle = false

    $: buttonName = reportToggle ? "Go Back" : "Status report"
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
        const conditions = [
            ...mainParameters, ...simulationParameters, ...dopplerLineshape, ...powerBroadening,
            ...einsteinCoefficient, ...collisionalCoefficient, ...rateCoefficients,
            {label:"currentLocation", value:currentLocation, id:window.getID()},
            {label:"filename", value:filename, id:window.getID()},
            {label:"writefile", value:writefile, id:window.getID()},
            {label:"variable", value:variable, id:window.getID()},
            {label:"range", value:range, id:window.getID()}
        ]

        dispatch('submit', { e, conditions })
        running=true
    }

    const style="width:12em; margin-bottom:1em;"

    let currentLocation = localStorage["thz_modal_location"] || localStorage["thz_location"] || ""
    
    let filename = `ROSAA_modal_${mainParameters[0].value}_${mainParameters[1].value}`

    function browse_folder() {
        browse({dir:true}).then(result=>{
            if (!result.canceled) { currentLocation= localStorage["thz_modal_location"] = result.filePaths[0] }

        })
    }

    let writefile = true

    let variable = "time", range = "1e12, 1e16, 10";
    const variablesList = ["time", "He density(cm3)", "a"]

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
            justify-self: center;
            align-self: center;
        }
    }

    .writefileCheck {
        border: solid 1px white;
        padding: 0.3em;
        width: 9em;
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

</style>

<Modal bind:active title="ROSAA modal" >


    <div slot="content">
        {#if reportToggle}
            <div class="content" style="white-space: pre-wrap;">{statusReport}</div>
    
        {:else}

            <div class="locationColumn">
                <button class="button is-link" id="thz_modal_filebrowser_btn" on:click={browse_folder}>Browse</button>

                <Textfield bind:value={currentLocation} label="Current location" />
                <Textfield bind:value={filename} label="filename" />
            </div>

            <div class="writefileCheck">

                <CustomCheckbox bind:selected={writefile} label="writefile" />
            </div>


            <div class="subtitle">Simulate signal(%) as a function of "{variable}"</div>
            <div class="variableColumn">

                <CustomSelect options={variablesList} bind:picked={variable} />
                <Textfield bind:value={range} label="Range (min, max, totalsteps)" />
            </div>


            <div class="subtitle">Main Parameters</div>

            {#each mainParameters as {label, value, id}(id)}

                <Textfield {style} bind:value {label}/>
            {/each}

            <div class="subtitle">Simulation parameters</div>
            {#each simulationParameters as {label, value, id}(id)}
                <Textfield {style} bind:value {label}/>
            {/each}

            <div class="subtitle">Doppler lineshape</div>
            {#each dopplerLineshape as {label, value, id}(id)}
                <Textfield {style} bind:value {label}/>
            {/each}

            <div class="subtitle">Lorrentz lineshape</div>
            {#each powerBroadening as {label, value, id}(id)}
                <Textfield {style} bind:value {label}/>
            {/each}

            <div class="subtitle">Einstein Co-efficients</div>
            {#each einsteinCoefficient as {label, value, id}(id)}
                <Textfield {style} bind:value {label}/>
            {/each}

            <div class="subtitle">Collisional rate constants</div>
            {#each collisionalCoefficient as {label, value, id}(id)}
                <Textfield {style} bind:value {label}/>
            {/each}

            <div class="subtitle">He attachment (K3) and diisociation (kCID) constants</div>
            {#each rateCoefficients as {label, value, id}(id)}
                <Textfield {style} bind:value {label}/>
            {/each}
        {/if}

    </div>

    <div class="align" slot="footerbtn">

        <button  class="button is-danger" on:click="{()=>{py&&running? py.kill() : console.log('pyEvent is not available')}}" >Stop</button>

        <button  class="button is-link" on:click="{(e)=>{reportToggle = !reportToggle}}" >{buttonName}</button>
        <button  class="button is-link" class:is-loading={running} on:click="{simulation}" on:pyEvent={pyEventHandle} on:pyEventClosed="{pyEventClosedHandle}" on:pyEventData={pyEventDataReceivedHandle}>Submit</button>

    </div>
    
</Modal>