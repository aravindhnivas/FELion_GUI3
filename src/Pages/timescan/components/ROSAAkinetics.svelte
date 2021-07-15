
<script>
    import {mainPreModal} from "../../../svelteWritable";
    import CustomSwitch from "../../../components/CustomSwitch.svelte"
    import CustomSelect from "../../../components/CustomSelect.svelte"
    import Textfield from '@smui/textfield'
    export let fileChecked=[], currentLocation="", kineticMode=true, timescanData={};
    let srgMode=true, pbefore=0, pafter=0, temp=5;

    // let numberDensity=0;
    let molecule="CD", tag="He", massOfReactants="", nameOfReactants="";
    let ratek3="k31", ratekCID="kCID1";

    let selectedFile = "", totalMass = [], requiredLength=0;
    let k3Guess = "1e-30", kCIDGuess="1e-15";
    let currentData = {}

    function computeParameters() {


        currentData = timescanData[selectedFile];
        if(currentData) {
            
            totalMass = Object.keys(currentData)
            totalMass = totalMass.slice(0, totalMass.length-1)
            
            massOfReactants = totalMass.join(", ")
            computeOtherParameters()
        }
    }

    function computeOtherParameters() {
        masses = massOfReactants.split(",").map(m=>m.trim())
        requiredLength = masses.length

        nameOfReactants =`${molecule}, ${molecule}${tag}`
        
        ratek3="k31", ratekCID="kCID1";

        for (let index = 2; index < requiredLength; index++) {
            ratek3 += `, k3${index}`
            ratekCID += `, kCID${index}`
            nameOfReactants += `, ${molecule}${tag}${index}`

        }
    }
    let masses;
    $: if(massOfReactants) {computeOtherParameters()}
    let calibrationFactor = 1;

    $: if(srgMode) {
        calibrationFactor = 1

        pbefore = Number(7e-5).toExponential(0)
    } else {
        calibrationFactor = 200

        pbefore = Number(1e-8).toExponential(0)
    
    }
    const constantValue = 4.2e17

    $: numberDensity = Number((constantValue*calibrationFactor*(pafter - pbefore))/(temp**0.5)).toExponential(3)
    $: if(selectedFile) {computeParameters()}
    async function kineticSimulation(e) {
    
        try {

            const pyfile = "ROSAA/kinetics.py"
            const nameOfReactantsArray = nameOfReactants.split(",").map(m=>m.trim())

            const data = {}
            massOfReactants.split(",").map(mass=>mass.trim()).forEach((mass, i)=>data[nameOfReactantsArray[i]]=currentData[mass])
            const args = [JSON.stringify({data, selectedFile, currentLocation, nameOfReactantsArray, ratek3, ratekCID, numberDensity, k3Guess, kCIDGuess, initialValues})]

            await computePy_func({e, pyfile, args, general:true})

        } catch (error) {$mainPreModal.modalContent = error;  $mainPreModal.open = true; $mainPreModal.type="danger"}
    }
    const pyEventClosed = (e) => {
        const {error_occured_py, dataReceived} = e.detail
        if(!error_occured_py) {$mainPreModal.open = true; $mainPreModal.modalContent = dataReceived; $mainPreModal.type="info"; }
    }
    let defaultInitialValues = true;

    let initialValues = ""
    $: if(defaultInitialValues && masses) {
            initialValues = masses.map(m=>currentData[m]["y"][0].toFixed(0))
    } else if(masses) {
        initialValues = Array(masses.length).fill(0)
        initialValues[0] = _.max(currentData[masses[0]]["y"]).toFixed(0)
    }
</script>

<div class="align animated fadeIn" class:hide={!kineticMode} >
    <div class="align">
        <CustomSwitch bind:selected={srgMode} label="SRG"/>
        <Textfield bind:value={pbefore} label="pbefore" />
        <Textfield bind:value={pafter} label="pafter" />
        <Textfield input$type="number" input$step="0.5" bind:value={calibrationFactor} label="calibrationFactor" />

        <Textfield input$type="number" input$step="0.1" bind:value={temp} label="temp(K)" />
        <Textfield bind:value={numberDensity} label="numberDensity" disabled />
    </div>

    <div class="align">

        <CustomSelect bind:picked={selectedFile} label="Filename" options={["", ...fileChecked]} style="min-width: 7em; "/>
        <Textfield bind:value={molecule} label="Molecule" />
    
        <Textfield bind:value={tag} label="tag" />
        <Textfield bind:value={massOfReactants} label="massOfReactants" />
        <Textfield bind:value={nameOfReactants} label="nameOfReactants" />

        <CustomSwitch bind:selected={defaultInitialValues} label="defaultInitialValues"/>
        
        <Textfield bind:value={initialValues} label="initialValues" />

        <Textfield bind:value={ratek3} label="ratek3" />
        
        <Textfield bind:value={k3Guess} label="k3Guess" />
        
        <Textfield bind:value={ratekCID} label="ratekCID" />
        
        <Textfield bind:value={kCIDGuess} label="kCIDGuess" />
    
        <button class="button is-link" on:click="{computeParameters}">Compute parameters</button>
        
        <button class="button is-link" on:click="{kineticSimulation}" on:pyEventClosed="{pyEventClosed}">Submit</button>
    </div>

</div>