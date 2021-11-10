
<script>
    // import {mainPreModal} from "../../../svelteWritable";
    import SeparateWindow from "../../../components/SeparateWindow.svelte";
    import { plot } from "../../../js/functions";
    import boltzman_distribution from "../functions/boltzman_distribution";
    import Textfield from '@smui/textfield';

    export let active, collisionalTemp=10;
    export let collisionalRateConstants, energyLevels, electronSpin, zeemanSplit, energyUnit;

    let initialTemp = 300, duration=600;
    
    let numberDensity="2e14";
    const title="Collisional cooling"
    const plotID = "collisionalDistributionPlot"
    
    let graphWindow=null, windowReady=false;


    let stepSize=0.1;
    async function computeCollisionalProcess(e) {
        try {
            const boltzmanDistribution = boltzman_distribution({energyLevels, trapTemp:initialTemp, electronSpin, zeemanSplit, energyUnit})
            const boltzmanDistributionValues = {}
            boltzmanDistribution.forEach(f=>boltzmanDistributionValues[f.label]=f.value)

            const collisionalRateConstantValues = {}
            collisionalRateConstants.forEach(f=>collisionalRateConstantValues[f.label]=f.value)

            const pyfile = "collisionalSimulation.py";

            const boltzmanDistributionCold = boltzman_distribution({energyLevels, trapTemp:collisionalTemp, electronSpin, zeemanSplit, energyUnit})
            const boltzmanData = {x:boltzmanDistributionCold.map(f=>f.label), y:boltzmanDistributionCold.map(f=>f.value), name:"boltzman"}

            const boltzmanPlotData = {boltzmanData}

            const args=[JSON.stringify({numberDensity, boltzmanDistributionValues, boltzmanDistributionCold:boltzmanData, duration, collisionalRateConstantValues})]

            const {data, collisionalBoltzmanPlotData, differenceFromBoltzman} = await computePy_func({e, pyfile, args})
            plot( `${title}: ${initialTemp}K --> ${collisionalTemp}K (${numberDensity}/cm3)`, "Time (s)", "Population", data, plotID)
            const combinedData = {...collisionalBoltzmanPlotData, ...boltzmanPlotData}
            

            plot( 
                ` Distribution: ${collisionalTemp}K`, 
                "Energy Levels", "Population", combinedData, 
                `${plotID}_collisionalBoltzman`, 

            )
            plot( 
                `Difference: Collisional - Boltzmann`, 
                
                "Energy Levels", "Difference", differenceFromBoltzman,
                
                `${plotID}_collisionalBoltzman_difference`,
            )

        } catch (error) { window.handleError(error) }
    }
    $: if (windowReady) {setTimeout(()=>graphWindow.focus(), 100)}

</script>

<style lang="scss">
    
    .header {
        display: flex;

        gap: 1em;
        margin-bottom: 1em;
    }

    .graph__container {

        display: flex;
        flex-direction: column;

        row-gap: 1em;

        padding: 1em;
    
    }

</style>

<SeparateWindow {title} bind:active bind:windowReady bind:graphWindow maximize={false}>
    <svelte:fragment slot="header_content__slot" >
        <div class="header">
            <Textfield bind:value={stepSize} label="stepSize"/>
            <Textfield bind:value={initialTemp} label="Initial temp (K)" input$type="number" input$step={stepSize} input$min=0/>

            <Textfield bind:value={collisionalTemp} label="Coll. temp (K)" input$type="number" input$step={stepSize} input$min=0.1 />
            <Textfield bind:value={duration} label="duration (in ms)" />
            <Textfield bind:value={numberDensity} label="Number density (cm-3)"/>
            <button class="button is-link" on:click={computeCollisionalProcess}>Compute</button>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">
        <div class="graph__container">
            <div id="{plotID}" class="graph__div"></div>

            <div id="{plotID}_collisionalBoltzman" class="graph__div"></div>
            
            <div id="{plotID}_collisionalBoltzman_difference" class="graph__div"></div>
        
        </div>
    </svelte:fragment>
</SeparateWindow>