
<script>
    import {mainPreModal} from "../../../svelteWritable";
    import CollisionalDistribution from "../windows/CollisionalDistribution.svelte";
    import {browse} from "../../../components/Layout.svelte";
    import Textfield from '@smui/textfield';
    import balance_distribution from "../functions/balance_distribution";

    export let collisionalCoefficient=[], collisionalCoefficient_balance=[], collisionalRateType="both", collisionalRates = [];
    export let energyLevels, electronSpin, zeemanSplit, energyUnit, numberDensity = "2e14", collisionalFilename, collisionalTemp;

    let collisionalWindow=false;
    
    const compteCollisionalBalanceConstants = () => {
        const balanceArgs  = {energyLevels, collisionalTemp,  electronSpin, zeemanSplit, energyUnit}
        collisionalCoefficient_balance = []

        collisionalCoefficient.forEach(coefficient=>{
            const {label, value} = coefficient
            const levelLabels = label.split(" --> ").map(f=>f.trim())
            let newLabel, newValue;
            newValue = value*balance_distribution({...balanceArgs, label})
            newLabel = `${levelLabels[1]} --> ${levelLabels[0]}`
        
            const alreadyComputed = _.find(collisionalCoefficient, (rate)=>rate.label==newLabel)
            if(!alreadyComputed)  {
                collisionalCoefficient_balance = [...collisionalCoefficient_balance, {label:newLabel, value:newValue.toExponential(3), id:getID()}]
             }
        })
    }
    $: collisionalRateConstants = [...collisionalCoefficient, ...collisionalCoefficient_balance]
    $: collisionalArgs = {collisionalRateConstants, energyLevels, electronSpin, zeemanSplit, energyUnit, collisionalTemp}
    const computeRate = (rate) => {
        rate.value *= numberDensity; 
        rate.value = rate.value.toExponential(3);
        return rate
    }

    $: if(collisionalRateConstants.length>0 && numberDensity) {
        collisionalRates = _.cloneDeep(collisionalRateConstants).map(computeRate)
    }

    async function browse_collisional_file() {
        const result = await browse({dir:false})
        if (result) { collisionalFilename = result[0] }
    }

    // let collisionlFile = ""
    
    let saveFilename = "collisional_rate_constants"
    // let collisionalTemp = 5
    const setID = (obj) => {
    
        obj.id = window.getID();
    
        return obj
    }

    const correctObjValue = (obj) => {
        obj.value = obj.value.toExponential(3)
        return obj
    
    }

    async function computeCollisionalFit(e) {
        try {
    
            if (collisionalFilename) {
                const pyfile = "ROSAA/collisionalFit.py"
                const args = [JSON.stringify({collisionalFilename, collisionalTemp, saveFilename, collisionalRateType})]
                const dataFromPython = await computePy_func({e, pyfile, args});
                const {rateConstants} = dataFromPython
    
                collisionalCoefficient = rateConstants.map(setID).map(correctObjValue)
            } else {browse_collisional_file()}
    
        } catch (error) { $mainPreModal = {modalContent:error, open:true} }
    }
    // const saveComputedCollisionalValues = () => {}

</script>

<style lang="scss">
    .sub_container__div {

        display: grid;
        grid-row-gap: 1em;
        .subtitle {place-self:center; margin-bottom: 0;}
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
    hr {background-color: #fafafa; margin: 0;}

</style>

<CollisionalDistribution {...collisionalArgs} bind:active={collisionalWindow} />

<div class="sub_container__div box">
    <div class="subtitle">Collisional rate constants</div>
    <div class="control__div ">
        <button class="button is-link " on:click={compteCollisionalBalanceConstants}>Compute balance rate</button>
        <button class="button is-link " on:click={()=>collisionalWindow=true}>Compute Collisional Cooling</button>
        <div class="align h-center">
            <Textfield bind:value={collisionalTemp} label="collisionalTemp"/>
            <button class="button is-link" on:click={browse_collisional_file}>Browse</button>
            <button class="button is-link" on:click={computeCollisionalFit}>Compute</button>
            <!-- <Textfield bind:value={saveFilename} label="saveFilename"/> -->
            <!-- <button class="button is-link" on:click={saveComputedCollisionalValues}>Save values</button> -->

        </div>

    </div>
    {#if collisionalCoefficient.length>0}

        <div class="content__div ">



        {#each collisionalCoefficient as {label, value, id}(id)}
            <Textfield bind:value {label}/>
        {/each}
        </div>

    {/if}

    {#if collisionalCoefficient_balance.length>0}

        <hr>
        <div class="content__div ">
            {#each collisionalCoefficient_balance as {label, value, id}(id)}
                <Textfield bind:value {label}/>

            {/each}
        </div>
    {/if}
    
    <hr>
    <div class="subtitle">Collisional Rates (per sec) </div>
    <div class="control__div">
        <Textfield bind:value={numberDensity} label="numberDensity (cm-3)"/>

    </div>
    <div class="content__div ">
        {#each collisionalRates as {label, value, id}(id)}
            <Textfield bind:value {label}/>
        {/each}

    </div>
</div>