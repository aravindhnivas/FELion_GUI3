
<script>
    import {mainPreModal} from "../../../svelteWritable";
    import Textfield from '@smui/textfield';
    import {PlanksConstant, SpeedOfLight} from "..//functions/constants";
    import {computeStatisticalWeight} from "../functions/balance_distribution";
    export let einsteinCoefficientA=[], einsteinCoefficientB=[];

    export let energyLevels, electronSpin, zeemanSplit, energyUnit;

    function computeEinsteinB() {
        const einsteinCoefficientB_emission = einsteinCoefficientA.map(({label, value})=>{

            const [final, initial] = label.split("-->").map(l=>l.trim())
            const {value:v0} = window._.find(energyLevels, (e)=>e.label==initial)
            const {value:v1} = window._.find(energyLevels, (e)=>e.label==final)
            
            let freq = parseFloat(v1) - parseFloat(v0) // in Hz or s-1
            

            energyUnit === "MHz" ? freq *= 1e6 : freq *= SpeedOfLight*100;
            const constTerm = SpeedOfLight**3/(8*Math.PI*PlanksConstant*freq**3)
            const B = constTerm*value
            return {label, value:B.toExponential(3)}
        })

        const einsteinCoefficientB_absorption = einsteinCoefficientB_emission.map(({label, value})=>{
            const [final, initial] = label.split("-->").map(l=>l.trim())
            const {Gi, Gf} = computeStatisticalWeight({electronSpin, zeemanSplit, final, initial});
            const weight = Gf/Gi
            const B = weight*parseFloat(value)
            const newLabel = `${initial} --> ${final}`
            return {label:newLabel, value:B.toExponential(3)}
        })

        einsteinCoefficientB = [...einsteinCoefficientB_emission, ...einsteinCoefficientB_absorption]
        
    }

    let lorrentz=0, gaussian=1, toggleEinsteinBcolumn=false;
    async function computeEinsteinBRate(e) {
        const args = [JSON.stringify({lorrentz, gaussian})]


        const pyfile = "ROSAA/voigt.py"

        try {
            const dataFromPython = computePy_func({e, pyfile, args})
        } catch (error) {
            $mainPreModal = {modalContent:error, open:true}
        }
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

<div class="sub_container__div box">
    <div class="subtitle">Einstein Co-efficients</div>

    <div class="control__div ">
        <button class="button is-link " on:click={computeEinsteinB}>Compute Einstein B</button>

    </div>

    
    <hr>
    <div class="subtitle">Einstein A Co-efficients</div>

    {#if einsteinCoefficientA.length>0}
        <div class="content__div ">
            {#each einsteinCoefficientA as {label, value}(label)}
                <Textfield bind:value {label} />
            {/each}
        </div>
    {/if}


    
    {#if einsteinCoefficientB.length>0}
        <hr>
        <div class="subtitle">Einstein B Co-efficients</div>
        <div class="control__div ">

            <button class="button is-link" on:click={()=>toggleEinsteinBcolumn = !toggleEinsteinBcolumn}>Compute rate constants</button>
            {#if toggleEinsteinBcolumn}
                <Textfield bind:value={lorrentz} label="lorrentz" />
                <Textfield bind:value={gaussian} label="gaussian"/>
                <button class="button is-link " on:click={computeEinsteinBRate}>Compute</button>
            {/if}
        </div>
        

        <div class="content__div ">
            {#each einsteinCoefficientB as {label, value}(label)}
                <Textfield bind:value {label} />
            {/each}
        </div>
    {/if}

</div>