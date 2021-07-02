
<script>
    import SeparateWindow from "../../../components/SeparateWindow.svelte";
    import { plot } from "../../../js/functions";
    import boltzmanDistribution from "../functions/boltzman_distribution";
    import Textfield from '@smui/textfield';
    // import {onMount} from 'svelte';

    export let active;
    export let energyLevels, trapTemp, electronSpin, zeemanSplit, energyUnit;
    const title="Boltzman Distribution"
    const plotID = "boltzmanDistributionPlot"

    let graphWindow=null, windowReady=false;
    
    let stepSize=0.1;

    function plotGraph() {
    
    
        const distribution = boltzmanDistribution({energyLevels, trapTemp, electronSpin, zeemanSplit, energyUnit})
        console.log(distribution)
        if(distribution) {
            const totalSum = _.sumBy(distribution, e=>e.value).toFixed(2)
            const energyLevel = distribution.map(e=>e.label)
            const populations = distribution.map(e=>e.value)
            const data = {  x: energyLevel, y: populations, mode: "lines+markers", showlegend:true, name:`Temp: ${trapTemp}K, Total: ${totalSum}`}
            dataToPlot = {data}
            plot( `${title}: ${trapTemp}K`, "Energy Levels", "Population", dataToPlot, plotID)
            // setTimeout(()=>graphWindow.focus(), 100)
        }
    }
    $: if (windowReady) {setTimeout(()=>graphWindow.focus(), 100);}
    $: if (windowReady && trapTemp>0) {plotGraph();}
    
</script>

<style>
    .header {
        display: flex;
        gap: 1em;
        margin-bottom: 1em;
    
    }
</style>

{#if active}

    <SeparateWindow {title} bind:active bind:windowReady bind:graphWindow >

        <svelte:fragment slot="header_content__slot" >
            <div class="header">
                
                <Textfield bind:value={stepSize} label="stepSize" style="width:auto;"/>
                <Textfield bind:value={trapTemp} label="temperature" input$type="number" input$step={stepSize} input$min=0 style="width:auto;"/>
                <button class="button is-link" on:click={plotGraph}>Compute</button>
            </div>


        </svelte:fragment>

        <svelte:fragment slot="main_content__slot">
            <div id="{plotID}"></div>

        </svelte:fragment>
    </SeparateWindow>
{/if}