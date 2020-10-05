
<script>
    import { createEventDispatcher } from 'svelte';
    import Modal from '../../components/Modal.svelte';
    import Textfield from '@smui/textfield';
    export let active=false;
    const dispatch = createEventDispatcher();

    let conditions = [
        {label:"power(W)", value:"2e-5", id:window.getID()},
        {label:"branching-ratio", value:0.5, id:window.getID()},
        {label:"trapTime(ms)", value:600, id:window.getID()},

        {label:"trapTemp(K)", value:5, id:window.getID()},
        {label:"He density(cm3)", value:"2e14", id:window.getID()},
        {label:"a", value:0.5, id:window.getID()},
        
        {label:"IonTemperature(K)", value:12, id:window.getID()},
        
        {label:"IonMass(amu)", value:14, id:window.getID()},
        {label:"cp", value:4e7, id:window.getID()},
        {label:"dipoleMoment(D)", value:0, id:window.getID()},
        {label:"numberOfLevel", value:3, id:window.getID()},
        {label:"totalIonCounts", value:1000, id:window.getID()},
        {label:"trap_area", value:5e-5, id:window.getID()},
        
        {label:"freq", value:453_521_850_000, id:window.getID()},
        
        {label:"k3", value:"9.6e-31, 2.9e-30", id:window.getID()},
        {label:"kCID", value:"6.7e-16, 1.9e-15", id:window.getID()},
        {label:"Collisional_q", value:"4.3242e-11, 3.4640e-11, 1.3013e-10", id:window.getID()},
        {label:"SpontaneousEmission", value:6.24e-4, id:window.getID()},
        {label:"Energy", value:"0, 15.127861, 45.373851", id:window.getID()},
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
        statusReport += "\n######## TERMINATED (simulation not compeleted) ########"
    }
</script>

<style>

</style>

<Modal bind:active title="ROSAA modal" >

    <div slot="content">


        {#if reportToggle}
            <div class="content" style="white-space: pre-wrap;">{statusReport}</div>
        {:else}
            
            {#each conditions as {label, value, id}(id)}
                <Textfield style="width:12em; margin-bottom:1em;" variant="outlined" type="text" bind:value {label}/>
            {/each}
        {/if}

    </div>

    <div class="align" slot="footerbtn">

        <button  class="button is-danger is-pulled-left" on:click="{()=>{py&&running? py.kill() : console.log('pyEvent is not available')}}" >Stop</button>

        <button  class="button is-link" on:click="{(e)=>{reportToggle = !reportToggle}}" >{buttonName}</button>
        <button  class="button is-link" class:is-loading={running} on:click="{(e)=> {dispatch('submit', { e, conditions }); running=true}}" on:pyEvent={pyEventHandle} on:pyEventClosed="{pyEventClosedHandle}" on:pyEventData={pyEventDataReceivedHandle}>Submit</button>

    </div>
    
</Modal>