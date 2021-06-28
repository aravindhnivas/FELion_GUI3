
<script>
    import SeparateWindow from "../../../components/SeparateWindow.svelte";
    import { plot } from "../../../js/functions";
    import boltzman_distribution from "../functions/boltzman_distribution";
    // import collisional_cooling from "../functions/collisional_cooling";
    import Textfield from '@smui/textfield';
    // import {onMount} from 'svelte';

    export let active;
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
            
            const args=[JSON.stringify(
                {numberDensity, boltzmanDistributionValues, duration, collisionalRateConstantValues}
            )]
            const dataFromPython = await computePy_func({e, pyfile, args})

            console.log(dataFromPython)
        } catch (error) {
            window.createToast(error, "danger")
        }
    }
    $: if (windowReady) {setTimeout(()=>graphWindow.focus(), 100)}

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
                <Textfield bind:value={initialTemp} label="temperature" input$type="number" input$step={stepSize} input$min=0 style="width:auto;"/>
                <Textfield bind:value={duration} label="duration (in ms)" input$type="number" input$step={stepSize} input$min=0 style="width:auto;"/>
                <Textfield bind:value={numberDensity} label="Number density" style="width:auto;"/>
                <button class="button is-link" on:click={computeCollisionalProcess}>Compute</button>
            </div>


        </svelte:fragment>

        <svelte:fragment slot="main_content__slot">
            <div id="{plotID}"></div>

        </svelte:fragment>
    </SeparateWindow>
{/if}