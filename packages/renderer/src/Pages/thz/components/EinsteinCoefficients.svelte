
<script>

    import {find}                           from "lodash-es"
    import Textfield                        from '@smui/textfield';
    import {PlanksConstant, SpeedOfLight}   from "../functions/constants";
    import {computeStatisticalWeight}       from "../functions/balance_distribution";

    
    export let einsteinCoefficientA=[]
    export let einsteinCoefficientB=[]
    export let einsteinB_rateComputed=false;
    
    export let lorrentz=0.320
    export let gaussian=0.210
    export let power="2e-5"
    export let trapArea="5e-5";
    export let energyUnit;
    export let zeemanSplit
    export let energyLevels
    export let electronSpin

    
    function computeEinsteinB() {
        einsteinB_rateComputed=false;

        const einsteinCoefficientB_emission = einsteinCoefficientA.map(({label, value})=>{
            const [final, initial] = label.split("-->").map(l=>l.trim())
            const {value:v0} = find(energyLevels, (e)=>e.label==initial)
            const {value:v1} = find(energyLevels, (e)=>e.label==final)
            let freq = parseFloat(v1) - parseFloat(v0) // in Hz or s-1
            energyUnit === "MHz" ? freq *= 1e6 : freq *= SpeedOfLight*100;

            const constTerm = SpeedOfLight**3/(8*Math.PI*PlanksConstant*freq**3)
            const B = constTerm*value
            return {label, value:B.toExponential(3), id:getID()}
        })

        const einsteinCoefficientB_absorption = einsteinCoefficientB_emission.map(({label, value})=>{
            const [final, initial] = label.split("-->").map(l=>l.trim())
            const {Gi, Gf} = computeStatisticalWeight({electronSpin, zeemanSplit, final, initial});
            const weight = Gf/Gi
            const B = weight*parseFloat(value)
            const newLabel = `${initial} --> ${final}`
            return {label:newLabel, value:B.toExponential(3), id:getID()}

        })
        einsteinCoefficientB = [...einsteinCoefficientB_emission, ...einsteinCoefficientB_absorption]
    }

    const computeGaussian = (x, sigma) => Math.E**(-(x**2) / (2*sigma**2)) / (sigma*Math.sqrt(2*Math.PI))
    const computeLorrentz = (x, gamma) => gamma / (Math.PI*(x**2 + gamma**2))

    const computePseudoVoigt = (x, sigma, gamma) => {
        const fG = (2*Math.sqrt(2*Math.log(2))) * sigma
        const fL = 2*gamma
        const f = (fG**5 + 2.69269*fG**4*fL + 2.42843*fG**3*fL**2 + 4.47163*fG**2*fL**3 + 0.07842*fG*fL**4 + fL**5)**(1/5)
        const eta = 1.36603*(fL/f) - 0.47719*(fL/f)**2 + 0.11116*(fL/f)**3

        console.log({fG, fL, f, eta})
        const lineshape = eta * computeLorrentz(x, gamma) + (1 - eta) * computeGaussian(x, sigma)
        return lineshape
    }

    $: voigtline = computePseudoVoigt(0, gaussian*1e6, lorrentz*1e6).toExponential(2)
    $: computeRates(voigtline)

    function computeRates(lineShape) {
        const constantTerm = power/(trapArea*SpeedOfLight)
        const norm = constantTerm*lineShape
        
        computeEinsteinB();

        einsteinCoefficientB = einsteinCoefficientB.map(rateconstant=>{
            rateconstant.value *= norm;
        
            rateconstant.value = rateconstant.value.toExponential(3)
            return rateconstant
        })
        
        einsteinB_rateComputed=true;
    }

    async function computeEinsteinBRate(e=null) {
        if(!lorrentz || !gaussian) return createToast("Compute gaussian and lorrentz parameters")
        const {lineShape} = await computePy_func({e, pyfile: "voigt", args: [JSON.stringify({lorrentz, gaussian})]})
        computeRates(lineShape)

    }

    $: if(einsteinCoefficientA) computeEinsteinB();

</script>

<div class="sub_container__div box">

    <div class="subtitle">Einstein Co-efficients</div>
    <hr>
    <div class="subtitle">Einstein A Co-efficients</div>

    {#if einsteinCoefficientA.length>0}
        <div class="content__div ">
            {#each einsteinCoefficientA as {label, value, id}(id)}
                <Textfield bind:value {label} />
            {/each}
        </div>
    {/if}

    <div class="control__div ">
        <button class="button is-link " on:click={computeEinsteinB}>Compute Einstein B</button>
    </div>
    
    {#if einsteinCoefficientB.length>0}
        <hr>

        <div class="subtitle">Einstein B Co-efficients</div>
        <div class="control__div ">
            <Textfield bind:value={voigtline} label="voigt lineshape" />
            <button class="button is-link " on:click={computeEinsteinBRate}>Compute rate constants</button>
        </div>

        <div class="content__div ">
            {#each einsteinCoefficientB as {label, value, id}(id)}
                <Textfield bind:value {label} />
            {/each}
        </div>
    {/if}

</div>


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
