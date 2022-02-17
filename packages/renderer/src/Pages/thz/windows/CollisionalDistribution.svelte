
<script>
    
    import Textfield                    from '@smui/textfield';
    import SeparateWindow               from "$components/SeparateWindow.svelte";
    import CustomTextSwitch             from "$components/CustomTextSwitch.svelte";
    import { plot }                     from "../../../js/functions";
    import boltzman_distribution        from "../functions/boltzman_distribution";
    import collisionCoolingODESolver    from "../functions/collisional_cooling?worker";
    import computePy_func               from "$src/Pages/general/computePy"



    export let active
    export let energyUnit;
    export let zeemanSplit
    export let energyLevels
    export let electronSpin
    export let numberOfLevels
    export let collisionalTemp=10;
    export let collisionalRateConstants

    
    const title="Collisional cooling"
    const plotID = "collisionalDistributionPlot"

    let duration=600;
    let initialTemp = 300
    let graphWindow=null
    let windowReady=false;
    let numberDensity="2e14";
    let totalSteps = 1000;
    async function computeCollisionalProcess(e) {

        try {
            
            const boltzmanDistribution = boltzman_distribution({
                trapTemp: initialTemp,
                energyUnit,
                zeemanSplit,
                energyLevels,
                electronSpin
            })
            
            const energyKeys = boltzmanDistribution.map(f=>f.label)

            const collisionalRateConstantValues = {}
            collisionalRateConstants.forEach(f=>collisionalRateConstantValues[f.label]=f.value)
            const {target} = e
            target?.classList.add("is-loading")

            const boltzmanDistributionCold = boltzman_distribution({
                    trapTemp: collisionalTemp,
                    energyUnit,
                    zeemanSplit,
                    energyLevels,
                    electronSpin,
            })

            const boltzmanDistributionValues = {}
            boltzmanDistribution.forEach(f=>boltzmanDistributionValues[f.label]=f.value)
            const boltzmanDistributionColdValues = {}
            boltzmanDistributionCold.forEach(f=>boltzmanDistributionColdValues[f.label]=f.value)
            const pyfile = "collisionalSimulation"
            const args = [JSON.stringify({boltzmanDistributionValues, boltzmanDistributionColdValues,
                numberDensity, collisionalRateConstantValues, duration, energyKeys, numberOfLevels
            })]

            const dataFromPython = await computePy_func({e, pyfile, args})
            const {data, collisionalBoltzmanPlotData, differenceFromBoltzman} = dataFromPython
            plot( 
                ` Distribution: ${collisionalTemp}K`, 
                "Time (s)", "Population", data, 
                plotID, 
            )

            plot(
                ` Distribution: ${collisionalTemp}K`, 
                "Energy Levels", "Population", collisionalBoltzmanPlotData, 
                `${plotID}_collisionalBoltzman`, 
            )

            plot(
                `Difference: Collisional - Boltzmann`, 
                "Energy Levels", "Difference", 
                differenceFromBoltzman,
                `${plotID}_collisionalBoltzman_difference`,
            )

            // return
            
            // const ODEWorker = new collisionCoolingODESolver()
            // ODEWorker.postMessage({
            //     duration,
            //     totalSteps,
            //     numberDensity,
            //     boltzmanDistribution,
            //     collisionalRateConstants
            // });
        
            // ODEWorker.onmessage = ({data: {finalData, error}}) => {
            //     if(error) return window.handleError(error)
            //     target.classList.remove("is-loading")
            //     if(!finalData) return
                
            //     console.log(finalData)

            //     plot( 
            //         ` Distribution: ${collisionalTemp}K`, 
            //         "Time (s)", "Population", finalData, 
            //         plotID, 
            //     )
            //     const boltzmanDistributionCold = boltzman_distribution({
            //         trapTemp: collisionalTemp,
            //         energyUnit,
            //         zeemanSplit,
            //         energyLevels,
            //         electronSpin,
            //     })

            //     const boltzmanDataCold = boltzmanDistributionCold.map(f=>f.value)
            //     const boltzmanData = {x: energyKeys, y: boltzmanDataCold, name:"boltzman"}

            //     const collisionalDataCold = []

            //     for (const key in finalData) {
            //         const coldValue = finalData[key].y.at(-1)
            //         collisionalDataCold.push(coldValue)
            //     }

            //     const collisionalData = {
            //         x: energyKeys, y: collisionalDataCold, name: "collisional"
            //     }
            //     const combinedData = {collisionalData, boltzmanData}
            //     console.log({finalData})
            //     plot(
            //     ` Distribution: ${collisionalTemp}K`, 
            //     "Energy Levels", "Population", combinedData, 
            //     `${plotID}_collisionalBoltzman`, 
            //     )

            //     const differenceFromBoltzman = []
            //     for (let i=0; i<boltzmanDataCold.length; i++) {
            //         const computeDifference = (boltzmanDataCold[i] - collisionalDataCold[i]).toFixed(2)
            //         differenceFromBoltzman.push(computeDifference)
            //     }

            //     plot(
            //         `Difference: Collisional - Boltzmann`, 
            //         "Energy Levels", "Difference", 
            //         {data: {x: energyKeys, y: differenceFromBoltzman, name:"Difference"}},
            //         `${plotID}_collisionalBoltzman_difference`,
            //     )
            // }

        } catch (error) { window.handleError(error) }
    }

    $: if (windowReady) {setTimeout(()=>graphWindow.focus(), 100)}
    
</script>

<SeparateWindow {title} bind:active bind:windowReady bind:graphWindow maximize={false} >

    <svelte:fragment slot="header_content__slot" >
        <div class="header">
            <CustomTextSwitch bind:value={initialTemp} label="Initial temp (K)" />
            <CustomTextSwitch bind:value={collisionalTemp} label="Coll. temp (K)" />
            <CustomTextSwitch bind:value={duration} label="duration (in ms)" />
            <Textfield bind:value={totalSteps} label="totalSteps" />
            <Textfield bind:value={numberDensity} label="Number density (cm-3)" />
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


<style lang="scss">
    .header {
        display: flex;
        gap: 1em;
        align-items: center;
    }
    
    .graph__container {
        display: flex;
        flex-direction: column;
        row-gap: 1em;

        padding: 1em;
    }
</style>

