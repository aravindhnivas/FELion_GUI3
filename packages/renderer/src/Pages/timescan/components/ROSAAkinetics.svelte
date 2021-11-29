
<script>

    import { tick } from "svelte"
    import Textfield from '@smui/textfield'
    import CustomSwitch from "$components/CustomSwitch.svelte"
    import CustomSelect from "$components/CustomSelect.svelte"
    import ModalTable from '$components/ModalTable.svelte'
    import PyButton from "$components/PyButton.svelte"
    import SeparateWindow from "$components/SeparateWindow.svelte"
    import Editor from "$components/Editor.svelte"
    import {computeKineticCodeScipy, computeKineticCodeSympy} from "../functions/computeKineticCode"

    export let fileChecked=[], currentLocation="", kineticMode=true, kineticData={};
    let fileCollections = []

    let srgMode=true, pbefore=0, pafter=0, temp=5;
    let molecule="CD", tag="He", massOfReactants="", nameOfReactants="";
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

        if(defaultInitialValues && masses) { 
            initialValues = [currentData?.[masses[0]]["y"][0].toFixed(0), ...Array(requiredLength-1).fill(1)]
         }
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
        const pDiff = Number(pafter) - Number(pbefore)
        calibrationFactor = Number(calibrationFactor)
        temp = Number(temp)

        numberDensity = Number((constantValue*calibrationFactor*pDiff)/(temp**0.5)).toExponential(3)
    }

    $: if (pbefore || pafter || temp || calibrationFactor || config_content[selectedFile]) {computeNumberDensity()}
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
        const config_file = pathJoin(currentLocation, config_file_ROSAAkinetics);

        fs.writeFile(config_file, save_config_content, function (err) {
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

            const config_file = pathJoin(currentLocation, config_file_ROSAAkinetics);
            if(fs.existsSync(config_file)) {
                config_content = JSON.parse(fs.readFileSync(config_file, "utf8"))
                window.createToast("Config file loaded: "+config_file_ROSAAkinetics, "warning");
                makeConfigArray(config_content)
                config_loaded = true

            } else {return window.createToast("config file not available", "danger")}

        } catch (error) {window.handleError(error)}
    }

    
    let pyfile = "ROSAA/kineticsCode"
    // let pyfile = "sympy"

    const kineticCodeFunction = {
        scipy: {fn: computeKineticCodeScipy, pyfile: "ROSAA/kineticsCode"}, 
        sympy: {fn: computeKineticCodeSympy, pyfile: "ROSAA/kineticsCode_sympy"}
    }
    async function kineticSimulation(e) {
        try {

            if(!selectedFile) return createToast("Select a file", "danger")
            if(Object.keys(kineticData).length === 0) return createToast("No data available", "danger")


            const nameOfReactantsArray = nameOfReactants.split(",").map(m=>m.trim())
            const data = {}

            massOfReactants.split(",")
                .map(mass=>mass.trim())
                .forEach((mass, i)=>data[nameOfReactantsArray[i]]=currentData[mass])
            if(typeof initialValues === "string") { initialValues = initialValues.split(",") }

            const args = [
                JSON.stringify({
                    data, selectedFile, temp, currentLocation, nameOfReactantsArray, ratek3, ratekCID, numberDensity, k3Guess, kCIDGuess, initialValues, kineticEditorLocation, kineticEditorFilename: kineticEditorFilename+".md"
                })
            ]
            await computePy_func({e, pyfile:pyfile+".py", args, general:true})

        } catch (error) {window.handleError(error);}
        
    }

    let pyProcesses=[];
    let defaultInitialValues = true;
    let initialValues = ""

    let adjustConfig = false;
    let configArray = []
    let configKeys = ["filename", "srgMode", "pbefore", "pafter", "calibrationFactor", "temp"]
    
    let editor;
    let kineticEditorFiletype = "kinetics"
    let kineticEditorLocation = db.get(`${kineticEditorFiletype}-report-md`) || ""
    let kineticEditorFilename = "report"
    // $: computeKineticCode = kineticCodeFunction[pyfile]?.fn;
    
</script>

<style lang="scss">
    .main_content__div {
        display: flex;
        flex-direction: column;
        gap: 1em;
        padding: 1em;
        
        .box { margin: 0;}
    }

</style>

<ModalTable 
    bind:active={adjustConfig} title="Config table" 
    bind:rows={configArray} keys={configKeys} userSelect={false} sortOption={true} >
    
    <svelte:fragment slot="footer">
        <button class="button is-link" on:click="{saveConfig}" >Save</button>
        <button class="button is-danger" on:click="{()=>adjustConfig=false}" >Close</button>
    </svelte:fragment>

</ModalTable>



<SeparateWindow bind:active={kineticMode} title="Kinetics">


    <svelte:fragment slot="header_content__slot">
        <div class="notice__div">Kinetics</div>
    </svelte:fragment>

    <svelte:fragment slot="main_content__slot">

        <div class="main_content__div">

            <div class="align box">
                <CustomSwitch bind:selected={srgMode} label="SRG"/>
                <Textfield bind:value={pbefore} label="pbefore" />
                <Textfield bind:value={pafter} label="pafter" />
                <Textfield input$type="number" input$step="0.5" bind:value={calibrationFactor} label="calibrationFactor" />
                <Textfield input$type="number" input$step="0.1" bind:value={temp} label="temp(K)" />
                <Textfield bind:value={numberDensity} label="numberDensity" disabled />
            </div>

            <div class="align box">
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

            <div class="report-editor-div" id="kinetics-editor__div">
                <Editor filetype={kineticEditorFiletype}
                    mount="#kinetics-editor__div" id="kinetics-editor"
                    mainTitle="Kinetic Code" bind:editor
                    bind:savefilename={kineticEditorFilename}
                    bind:location={kineticEditorLocation}
                >

                    <svelte:fragment slot="btn-row">
                        <!-- <CustomSelect bind:picked={pyfile} label="computeFunction" options={["scipy", "sympy"]}  /> -->
                        <button class="button is-warning" 
                            on:click={()=>{
                                if(!massOfReactants) return window.createToast("No data available", "danger")
                                
                                const dataToSet = computeKineticCodeScipy({initialValues, nameOfReactants, ratek3, ratekCID})
                                // const dataToSet = computeKineticCode({initialValues, nameOfReactants, ratek3, ratekCID})
                                if(dataToSet) {editor?.setData(dataToSet)}
                            }}>compute</button>
                    </svelte:fragment> 
                </Editor>
            </div>
        </div>

    </svelte:fragment>

    <svelte:fragment slot="footer_content__slot" >

        {#if pyProcesses.length}
            <button class="button is-danger" 
                on:click="{()=>{pyProcesses.at(-1).kill(); pyProcesses.pop()}}"
            >Stop</button>
            <!-- <div>{pyProcesses.length} process running</div> -->
        {/if}

        <Textfield bind:value={pyfile} label="pyfile" />
        
        <button class="button is-link" on:click="{computeParameters}" >Compute parameters</button>
        <button class="button is-link" on:click="{loadConfig}">loadConfig</button>
        <i class="material-icons" on:click="{()=> adjustConfig = true}">settings</i>
        <PyButton on:click={kineticSimulation} bind:pyProcesses showLoading={true}/>
    </svelte:fragment>

</SeparateWindow>
