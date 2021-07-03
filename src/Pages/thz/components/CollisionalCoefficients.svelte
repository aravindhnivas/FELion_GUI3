
<script>
    // import {mainPreModal} from "../../../svelteWritable";
    import CollisionalDistribution from "../windows/CollisionalDistribution.svelte";
    import Textfield from '@smui/textfield';
    import CustomSelect from "../../../components/CustomSelect.svelte";
    import balance_distribution from "../functions/balance_distribution";

    export let collisionalCoefficient=[], collisionalCoefficient_balance=[], collisionalRateType="both";
    export let energyLevels, electronSpin, zeemanSplit, energyUnit, trapTemp;
    $: deexcitation = collisionalRateType==="deexcitation";
    let collisionalWindow=false;
    
    let numberDensity = "2e14";

    function changeCollisionalRateType() {
    
        collisionalCoefficient = collisionalCoefficient.map(level=>{

    
            const level_arr = level.label.split(" --> ")
            level.label = `${level_arr[1]} --> ${level_arr[0]}`
            return level
        })
    }

    const compteCollisionalBalanceConstants = () => {
        const balanceArgs  = {energyLevels, trapTemp,  electronSpin, zeemanSplit, energyUnit}
        console.log(balanceArgs)
        collisionalCoefficient_balance = collisionalCoefficient.map(coefficient=>{
            const {label, value} = coefficient
            const levelLabels = label.split(" --> ").map(f=>f.trim())
            let newLabel, newValue;
            if(deexcitation) {
                const [excitedLevel, groundLevel] = levelLabels

                newValue = value*balance_distribution({...balanceArgs, groundLevel, excitedLevel})
                newLabel = `${groundLevel} --> ${excitedLevel}`
                
            } else {

                const [groundLevel, excitedLevel] = levelLabels
                newValue = value*balance_distribution({...balanceArgs, groundLevel:excitedLevel, excitedLevel:groundLevel})
                newLabel = `${excitedLevel} --> ${groundLevel}`


            }
            // console.log(value, newValue)
            return {label:newLabel, value:newValue.toExponential(3), id:getID()}
        })

    }

    $: collisionalRateConstants = [...collisionalCoefficient, ...collisionalCoefficient_balance]
    $: collisionalArgs = {collisionalRateConstants, energyLevels, electronSpin, zeemanSplit, energyUnit}

    function computeRateConstant() {

        const compute = (rate) => {
            rate.value *= numberDensity; 
            rate.value = rate.value.toExponential(3);
            return rate
        }

        collisionalCoefficient = collisionalCoefficient.map(rate=>compute(rate))
        collisionalCoefficient_balance = collisionalCoefficient_balance.map(rate=>compute(rate))
            
    }
</script>

<style lang="scss">
    .sub_container__div {

        display: grid;
        grid-row-gap: 1em;

        .subtitle {place-self:center;}
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
        <CustomSelect options={["deexcitation", "excitation", "both"]} bind:picked={collisionalRateType} on:change={changeCollisionalRateType}/>
        <button class="button is-link " on:click={compteCollisionalBalanceConstants}>Compute balance rate</button>
        <button class="button is-link " on:click={()=>collisionalWindow=true}>Compute Collisional Cooling</button>
    </div>

    <div class="control__div">
        <Textfield bind:value={numberDensity} label="numberDensity (cm-3)"/>
        <button class="button is-link " on:click={computeRateConstant}>Compute rate constants</button>
    </div>

    {#if collisionalCoefficient.length>0}
        <div class="content__div ">
            {#each collisionalCoefficient as {label, value}(label)}
                <Textfield bind:value {label}/>
            {/each}
        </div>
    
    {/if}

    {#if collisionalCoefficient_balance.length>0}
        <div class="content__div ">

            <hr><hr>
            


            {#each collisionalCoefficient_balance as {label, value}(label)}
            
                <Textfield bind:value {label}/>
            {/each}

        </div>

    {/if}

</div>