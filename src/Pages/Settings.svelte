<script>

    // Importing modules
    import {pythonpath, pythonscript, pyVersion, github, backupName} from "./settings/svelteWritables";
    import Textfield from '@smui/textfield';
    import {onMount} from "svelte";

    import CustomDialog from "../components/CustomDialog.svelte"
    import CustomSelect from '../components/CustomSelect.svelte';
    import PreModal from "../components/PreModal.svelte";
    import {download} from "./settings/donwloadUpdate";

    import {InstallUpdate} from "./settings/installUpdate";
    
    import {updateCheck} from "./settings/updateCheck";

    import {resetPyConfig, updatePyConfig} from "./settings/checkPython";

    import {backupRestore} from "./settings/backupAndRestore";
    import {tick} from "svelte";

///////////////////////////////////////////////////////

    const backup = (event) => {
        backupRestore({event, method:"backup"})
            .then(()=>console.log("Backup Completed"))
            .catch((err)=>{preModal.modalContent = err; preModal.open = true})
    }

    const restore = (event) => {
        backupRestore({event, method:"restore"})
        .then(()=>console.log("Restore Completed"))
        .catch((err)=>{preModal.modalContent = err; preModal.open = true})
    }

    let selected = "Configuration"
    
    const navigate = (e) => {selected = e.target.innerHTML}

    let pythonpathCheck;

    onMount(()=>{
    
    setTimeout(async ()=>{

        await tick()
        checkPython()

            .then(res=>{ $pyVersion = res; console.log("Python path is valid")})
            .catch(()=>pythonpathCheck.open() )}
        , 1000)

        updateCheck({info:false})
        
        setInterval(()=>{updateCheck({info:false})}, 1*1000*60*15)
    })

    const handlepythonPathCheck = () => { console.log("Python path checking done") }
    
    const update = async () => {

        try {

            const updateFolder = path.resolve(__dirname, "..", "update")
            let target = document.getElementById("updateBtn")
            
            target.classList.toggle("is-loading")

            if (!fs.existsSync(updateFolder)) {fs.mkdirSync(updateFolder)}
            
            await download(updateFolder)
            
            InstallUpdate(target, updateFolder)
        } catch (err) {preModal.modalContent = err.stack; preModal.open = true}
        
    }

    let preModal = {};

</script>


<style>

    section { margin: 0; padding: 0; }
    .side-panel, .main-panel {height: calc(100vh - 7em);}
    .box { background-color: #6a50ad8a}
    .main-panel {margin: 0 5em;}

    .left .title { letter-spacing: 0.1em; text-transform: uppercase; padding: 0.5em;
        font-size: larger; cursor: pointer; border-radius: 20px 0; margin-bottom: 1em;
    }

    .container {padding: 2em; display: grid;}
    .clicked {border-left: 2px solid #fafafa; border: solid 1px;}
    .right > div {display: none;}
    .active {display: block!important; }
    .right .title {letter-spacing: 0.1em; text-transform: uppercase;}
    * :global(option) { color: black; }

</style>

<PreModal bind:preModal />

<CustomDialog id="pythonpath_Check" bind:dialog={pythonpathCheck} on:response={handlepythonPathCheck} title={"Python path is not valid"} content={"Change it in Settings --> Configuration"} label1="Okay" label2="Cancel" />

<section class="section animated fadeIn" id="Settings" style="display:none">

    <div class="columns">
        <div class="column side-panel is-2-widescreen is-3-desktop is-4-tablet box adjust-right">
            <div class="container left">
                <div class="title nav hvr-glow" class:clicked={selected==="Configuration"} on:click={navigate}>Configuration</div>
                <div class="title nav hvr-glow" class:clicked={selected==="Update"} on:click={navigate}>Update</div>
                <div class="title nav hvr-glow" class:clicked={selected==="About"} on:click={navigate}>About</div>
            </div>
        </div>

        <div class="column main-panel box">
            <div class="container right">

                <!-- Configuration -->
                <div class="content animated fadeIn" class:active={selected==="Configuration"}>
                    <h1 class="title">Configuration</h1>
                    <div class="subtitle">{$pyVersion}</div>
                    <Textfield style="margin-bottom:1em;" bind:value={$pythonpath} label="Python path" />
                    <Textfield style="margin-bottom:1em;" bind:value={$pythonscript} label="Python script path" />
                    <button class="button is-link" on:click={resetPyConfig}>Reset</button>
                    <button class="button is-link" on:click={updatePyConfig}>Save</button>
                </div>

                <!-- Update -->
                <div class="content animated fadeIn" class:active={selected==="Update"}>
                    <h1 class="title">Update</h1>

                    <div class="subtitle">Current Version {window.currentVersion}</div>
                    <div class="content">
                        <Textfield style="width:7em; margin-right:2em;" bind:value={$github.username} label="Github username" />
                        <Textfield style="width:7em; margin-right:2em;" bind:value={$github.repo} label="Github Repo" />
                        <CustomSelect bind:picked={$github.branch} label="Github branch" options={["master", "developer"]}/>
                    </div>

                    <div class="content">
                        <button class="button is-link" id="updateCheckBtn" on:click="{updateCheck}">Check update</button>
                        <button class="button is-link" id="updateBtn" on:click={update}>Update</button>
                    </div>


                    <div class="content">
                        <Textfield style="width:30%; margin-right:2em;" bind:value={$backupName} label="Github username" />
                        <button class="button is-link" on:click={backup}>Backup</button>
                        <button class="button is-link" on:click={restore}>Restore</button>
                    </div>
                    
                </div>


                <!-- About -->
                <div class="content animated fadeIn" class:active={selected==="About"}>
                    <h1 class="title">About</h1>
                </div>
                
            </div>
        </div>
    </div>
    
</section>