
<script>
    import {cloneDeep, find}                           from "lodash-es"
    import Textfield                        from '@smui/textfield';
    import computePy_func                   from "$src/Pages/general/computePy"
    import BoxComponent                     from "./BoxComponent.svelte";
    import {PlanksConstant, SpeedOfLight}   from "../functions/constants";
    import {computeStatisticalWeight}       from "../functions/balance_distribution";

    export let einsteinCoefficientA=[]
    export let einsteinCoefficientB=[]
    export let einsteinCoefficientB_rateConstant=[]

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
        try {
            // await tick()
            console.log("Computing Einstein B constants", {einsteinCoefficientA, energyLevels})
            einsteinB_rateComputed=false;
            const einsteinCoefficientB_emission = einsteinCoefficientA.map(({label, value})=>{
                const [final, initial] = label.split("-->").map(l=>l.trim())
                const v0 = find(energyLevels, (e)=>e?.label==initial)?.value
                const v1 = find(energyLevels, (e)=>e?.label==final)?.value
                const freq = parseFloat(v1) - parseFloat(v0)
                const freqInHz = energyUnit === "MHz" ? freq * 1e6 : freq * SpeedOfLight*100;

                const constTerm = SpeedOfLight**3/(8*Math.PI*PlanksConstant*freqInHz**3)
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
            einsteinCoefficientB_rateConstant = cloneDeep(einsteinCoefficientB)
        } catch (error) {window.handleError(error)}
    }

    const computeGaussian = (x, sigma) => Math.E**(-(x**2) / (2*sigma**2)) / (sigma*Math.sqrt(2*Math.PI))
    const computeLorrentz = (x, gamma) => gamma / (Math.PI*(x**2 + gamma**2))

    const computePseudoVoigt = (x, fG, fL) => {
        
        const f = (fG**5 + 2.69269*fG**4*fL + 2.42843*fG**3*fL**2 + 4.47163*fG**2*fL**3 + 0.07842*fG*fL**4 + fL**5)**(1/5)
        const eta = 1.36603*(fL/f) - 0.47719*(fL/f)**2 + 0.11116*(fL/f)**3

        console.log({fG, fL, f, eta})
        const sigma = fG / (2*Math.sqrt(2*Math.log(2)))
        const gamma = fL / 2
        const lineshape = eta * computeLorrentz(x, gamma) + (1 - eta) * computeGaussian(x, sigma)
        return lineshape
    }

    $: voigtline = computePseudoVoigt(0, gaussian*1e6, lorrentz*1e6).toExponential(2)
    // $: computeRates(voigtline)

    function computeRates(lineShape, compute=true) {
        if(compute) {computeEinsteinB()}
        if(einsteinCoefficientB.length < 1) return
        const constantTerm = parseFloat(power)/(parseFloat(trapArea)*SpeedOfLight)
        const norm = constantTerm*lineShape

        einsteinCoefficientB = einsteinCoefficientB.map(rateconstant => ({...rateconstant, value: Number(rateconstant.value*norm).toExponential(3) }) )
        einsteinB_rateComputed = einsteinCoefficientB.length > 0;
    
    }

    async function computeEinsteinBRate(e=null) {
        if(!lorrentz || !gaussian) return createToast("Compute gaussian and lorrentz parameters")
        const dataFromPython = await computePy_func({e, pyfile: "voigt", args: [JSON.stringify({lorrentz, gaussian})]})

        if(!dataFromPython) return
        const lineShape = dataFromPython?.lineShape
        console.log(lineShape.toExponential(2))
        computeRates(lineShape)
    }

    $: if(einsteinCoefficientA.length) {
        computeEinsteinB();
        if(voigtline) {computeRates(voigtline, false)}

    }

</script>


<BoxComponent title="Einstein Co-efficients" loaded={einsteinCoefficientA.length > 0 && einsteinCoefficientB.length > 0 && einsteinB_rateComputed } >

    <!-- <hr> -->
    <div class="align h-center subtitle">Einstein A Co-efficients</div>

    {#if einsteinCoefficientA.length>0}
        {#each einsteinCoefficientA as {label, value, id}(id)}
            <Textfield bind:value {label} />
        {/each}
    {/if}

    <div class="align h-center ">
        <button class="button is-link" on:click={computeEinsteinB}>

            {#if einsteinCoefficientB.length<1}
                <i class="material-icons">sync_problem</i>
            {/if}
            Compute Einstein B
        </button>
    </div>

    
    {#if einsteinCoefficientB.length>0}
    
        <hr>

        <div class="align h-center subtitle">Einstein B Co-efficients</div>
        <div class="align h-center">
            <Textfield bind:value={voigtline} label="voigt lineshape (Hz)" />
            <button class="button is-link " on:click={computeEinsteinBRate}>
                {#if !einsteinB_rateComputed}
                    <i class="material-icons">sync_problem</i>
                {/if}
                Compute rate constants
            </button>
        </div>

        <div class="align h-center">
            {#each einsteinCoefficientB as {label, value, id}(id)}
                <Textfield bind:value {label} />
            {/each}
        </div>
    {/if}
</BoxComponent>