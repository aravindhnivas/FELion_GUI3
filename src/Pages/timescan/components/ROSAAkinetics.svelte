
<script>
    import {mainPreModal} from "src/svelteWritable.js";
    import CustomSwitch from "components/CustomSwitch.svelte"
    import CustomSelect from "components/CustomSelect.svelte"
    import Textfield from '@smui/textfield'
    import ModalTable from 'components/ModalTable.svelte'

    import {Icon} from '@smui/icon-button';
    import { tick } from "svelte";
    export let fileChecked=[], currentLocation="", kineticMode=true, kineticData={};
    let fileCollections = []

    let srgMode=true, pbefore=0, pafter=0, temp=5;
    let molecule="CD^+", tag="He", massOfReactants="", nameOfReactants="";
    let ratek3="k31", ratekCID="kCID1";
    let selectedFile = "", totalMass = [], requiredLength=0;
    let k3Guess = "1e-30", kCIDGuess="1e-15";


    let currentData = {}
    $: if(fileChecked && kineticData && kineticMode) {
        const keys = Object.keys(kineticData)
        fileCollections = fileChecked.filter(filename=>keys.includes(filename))
    }

    function computeParameters() {
        currentData = kineticData[selectedFile];
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
        if(defaultInitialValues && masses) { initialValues = [currentData[masses[0]]["y"][0].toFixed(0), ...Array(requiredLength-1).fill(1)] }

        nameOfReactants =`${molecule}, ${molecule}${tag}`
        
        ratek3="k31", ratekCID="kCID1";

        for (let index = 2; index < requiredLength; index++) {
            ratek3 += `, k3${index}`
            ratekCID += `, kCID${index}`
            nameOfReactants += `, ${molecule}${tag}_${index}`

        }
    }
    let masses;
    $: if(massOfReactants) {computeOtherParameters()}
    let calibrationFactor = 1;
    let update_pbefore = true;
    $: if(srgMode) {
        calibrationFactor = 1
        if(update_pbefore) pbefore = Number(7e-5).toExponential(0)
    } else {
        calibrationFactor = 200
        if(update_pbefore) pbefore = Number(1e-8).toExponential(0)
    }

    

    let numberDensity = 0;
    const computeNumberDensity = async () => {
        await tick()
        const constantValue = 4.2e17
        numberDensity = Number((constantValue*calibrationFactor*(pafter - pbefore))/(temp**0.5)).toExponential(3)

    }


    $: if (pafter || temp || config_content[selectedFile]) {computeNumberDensity()}
    $: if(selectedFile || kineticData) {computeParameters()}

    let config_file_ROSAAkinetics="config_file_ROSAAkinetics.json";
    let config_content = {}

    function saveConfig() {
        if(!fs.existsSync(currentLocation)) {return window.createToast("Invalid location or filename", "danger")}

        const keys = configKeys.slice(1, configKeys.length)

        configArray.forEach(content => {
            const filename = content["filename"]
        
            const newKeyValue = {}
            keys.forEach(key=>{newKeyValue[key]=content[key]})
            config_content[filename] = newKeyValue
        })
        const save_config_content = JSON.stringify(config_content, null, 4)
        const config_file = path.join(currentLocation, config_file_ROSAAkinetics);
        fs.writeFile(config_file, save_config_content, "utf8", function (err) {
            if (err) return window.createToast("Error occured while saving file", "danger");

            window.createToast("Config file saved"+config_file_ROSAAkinetics, "warning")
        });
    }

    function makeConfigArray(obj) {
        const keys = Object.keys(obj)
        configArray = keys.map(
            filename=>{

                const id = window.getID()
                return {filename, id, ...obj[filename]}
            }
        )
        
        const fileCheckedRemaining = _.difference(fileChecked, keys)

        fileCheckedRemaining.forEach(filename=>{
            const id = window.getID()

            if (filename in obj) {
                const currentValue = {filename, id}
                const currentObj = obj[filename]
                configKeys.forEach(key=>{
                    if(key in currentObj) {currentValue[key] = currentObj[key]}
                })
                configArray = [...configArray, currentValue]
            } else if (filename) {
                const currentValue = {filename, id}
                configKeys.forEach(key=>{if(key !== "filename") {currentValue[key] = ""}})
                configArray = [...configArray, currentValue]
            
            }
            
        })
    }

    function updateConfig() {



        update_pbefore = false;
        
        try {
            if(!config_content[selectedFile]) {
        
                return window.createToast("config file not available for selected file: "+selectedFile, "danger")
            }
            ({srgMode, pbefore, pafter, calibrationFactor, temp} = config_content[selectedFile]);

            srgMode = JSON.parse(srgMode);
        } catch (error) {
            
            console.error(error.stack)
            window.createToast("Error while reading the values: Check config file", "danger");
        }
    }

    $: if(selectedFile && config_content && config_loaded) {updateConfig()}
    let config_loaded = false;

    async function loadConfig() {
        try {
            const config_file = path.join(currentLocation, config_file_ROSAAkinetics);
            if(fs.existsSync(config_file)) {
                config_content = JSON.parse(fs.readFileSync(config_file, "utf8"))
                window.createToast("Config file loaded: "+config_file_ROSAAkinetics, "warning");
                makeConfigArray(config_content)
                config_loaded = true

            } else {
                return window.createToast("config file not available", "danger")
            }
        } catch (error) {
            console.log(error)
            mainPreModal.error(error.stack)
        }
    }

    async function kineticSimulation(e) {
        try {

            if(!selectedFile) return createToast("Select a file", "danger")
            if(Object.keys(kineticData).length === 0) return createToast("No data available", "danger")
            const pyfile = "ROSAA/kinetics.py"
            const nameOfReactantsArray = nameOfReactants.split(",").map(m=>m.trim())
            const data = {}

            massOfReactants.split(",").map(mass=>mass.trim()).forEach((mass, i)=>data[nameOfReactantsArray[i]]=currentData[mass])

            if(typeof initialValues === "string") { initialValues = initialValues.split(",") }
            const args = [JSON.stringify({data, selectedFile, temp, currentLocation, nameOfReactantsArray, ratek3, ratekCID, numberDensity, k3Guess, kCIDGuess, initialValues})]

            pyEventCounter++;
            await computePy_func({e, pyfile, args, general:true})


        } catch (error) {mainPreModal.error(error.stack || error);}
    }

    let pyEventCounter = 0
    const pyEventClosed = (e) => {
        pyEventCounter--;
        const {error_occured_py, dataReceived} = e.detail
        if(!error_occured_py) {mainPreModal.info(dataReceived)}
    }
    
    let defaultInitialValues = true;
    let initialValues = ""
    let adjustConfig = false;
    let configArray = []
    let configKeys = ["filename", "srgMode", "pbefore", "pafter", "calibrationFactor", "temp"]
</script>

<ModalTable bind:active={adjustConfig} title="Config table" 
    bind:rows={configArray} keys={configKeys} userSelect={false} sortOption={true} >

    <svelte:fragment slot="footer">

        <button class="button is-link" on:click="{saveConfig}" >Save</button>

        <button class="button is-link" on:click="{()=>adjustConfig=false}" >Close</button>
    </svelte:fragment>

</ModalTable>

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
        <CustomSelect bind:picked={selectedFile} label="Filename" options={["", ...fileCollections]} style="min-width: 7em; "/>
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

    </div>

    <div class="align v-center">
        <button class="button is-link" on:click="{computeParameters}" >Compute parameters</button>
        <button class="button is-link" on:click="{loadConfig}">loadConfig</button>
        <Icon class="material-icons" on:click="{()=> adjustConfig = true}">settings</Icon>
        <button class="button is-link" on:click="{kineticSimulation}" on:pyEventClosed="{pyEventClosed}">Submit</button>
        {#if pyEventCounter}

            <div class="subtitle">{pyEventCounter} process running</div>
        
        {/if}
    
    </div>

</div>