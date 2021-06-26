
<script>
    import SeparateWindow from "../../../components/SeparateWindow.svelte";
    import { plot } from "../../../js/functions";
    import boltzmanDistribution from "../functions/boltzman_distribution";
    import Textfield from '@smui/textfield';
    

    export let active;
    export let boltzmanArgs, energyLevels;
    let {trapTemp}=boltzmanArgs;
    const title="Boltzman Distribution"

    const plotID = "boltzmanDistributionPlot"
    let stepSize=0.1;
    function plotGraph() {

        boltzmanArgs.trapTemp = trapTemp


        console.log(boltzmanArgs)
        const distribution = boltzmanDistribution({energyLevels, ...boltzmanArgs})
        const totalSum = _.sumBy(distribution, e=>e.value).toFixed(2)
        const energyLevel = distribution.map(e=>e.label)
        const populations = distribution.map(e=>e.value)

        const data = {  x: energyLevel, y: populations, mode: "lines+markers", showlegend:true, name:`Temp: ${trapTemp}K, Total: ${totalSum}`}
        dataToPlot = {data}
        plot( `${title}: ${trapTemp}K`, "Energy Levels", "Population", dataToPlot, plotID)
    }
    

</script>

<style>
    .header {
        display: flex;
        gap: 1em;
        margin-bottom: 1em;
    
    }
</style>


{#if active}
    <SeparateWindow  {title} bind:active >

        <svelte:fragment slot="header_content__slot" >
        
            <div class="header">
                
                <Textfield bind:value={stepSize} label="stepSize" style="width:auto;"/>
                <Textfield bind:value={trapTemp} label="temperature" input$type="number" input$step={stepSize} input$min=0 style="width:auto;"/>
                <button class="button is-link" on:click={plotGraph}>Compute</button>
            </div>


        </svelte:fragment>

        <svelte:fragment slot="main_content__slot" >
            <div use:plotGraph id="{plotID}"></div>
        </svelte:fragment>

    </SeparateWindow>

{/if}