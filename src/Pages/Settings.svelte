<script>

    // Importing modules
    import {pythonpath, pythonscript, pyVersion, github, backupName, developerMode} from "./settings/svelteWritables";
    import {activateChangelog, windowLoaded} from "../js/functions"
    import Textfield from '@smui/textfield';
    import {onMount} from "svelte";
    import { fade } from 'svelte/transition';
    import CustomDialog from "../components/CustomDialog.svelte"
    import CustomSelect from '../components/CustomSelect.svelte';
    import PreModal from "../components/PreModal.svelte";
    import Changelog from "../components/Changelog.svelte";

    import {download} from "./settings/donwloadUpdate";
    
    import {InstallUpdate} from "./settings/installUpdate";
    
    import { Button, Message, Snackbar } from 'svelma'

    
    import {updateCheck} from "./settings/updateCheck";
    import {resetPyConfig, updatePyConfig} from "./settings/checkPython";
    import {backupRestore} from "./settings/backupAndRestore";
    import {tick} from "svelte";
    import Terminal from '../components/Terminal.svelte';

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

    let selected = "Update"
    
    const navigate = (e) => {selected = e.target.innerHTML}

    let pythonpathCheck;

    
    onMount(()=>{
        setTimeout(async ()=>{

            await tick()
            checkPython()
                .then(res=>{ $pyVersion = res; console.log("Python path is valid")})

                .catch(()=>pythonpathCheck.open() )

            } , 1000)


        updateCheck({info:false})
        const timer_for_update = setInterval(()=>{updateCheck({info:false})}, 1*1000*60*15)
        return ()=>{clearInterval(timer_for_update)}

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
    let commandToRun = "", commandArgsToRun = "";

    
    // $: if(!$developerMode) {
    //     console.log("Setting default pathon path")
    //     $pythonpath = path.resolve(__dirname, "../python3/python")
    //     $pythonscript = path.resolve(__dirname, "assets/python_files")
    // } else {
    //     window.showStackContext({title:"Warning", text:"If python path is invalid, the program might not work", type:"error"});

    // }

    $: if($developerMode&&$windowLoaded) {window.showStackContext({title:"Warning", text:"If python path is invalid, the program might not work", type:"error"});}


    $: if($github.branch === "developer") {
        window.showStackContext({title:"Warning", text:"Developer channel may not be stable and contains bugs.", type:"error"});

    }

</script>


<style lang="scss">

    section { margin: 0; padding: 0; }
    .side-panel, .main-panel {height: calc(100vh - 7em);}
    .box { background-color: #6a50ad8a}
    .main-panel {margin: 0 5em;}

    .left .title { 
        letter-spacing: 0.1em; text-transform: uppercase; padding: 0.5em; text-align: center;
        font-size: larger; cursor: pointer; margin-bottom: 1em; border-radius: 20px; 
    }
    
    .clicked {border-left: 2px solid #fafafa; border: solid 1px;}
    
    * :global(option) { color: black; }
    .container {padding: 2em; display: grid;}
    .container .left {place-content: center;}

    .right.title {
        letter-spacing: 0.1em; 
        text-transform: uppercase;
        border-bottom: solid;
        margin-bottom: 2em;
        padding-bottom: 0.2em;
        width: fit-content;
    }

</style>
<PreModal bind:preModal />
<CustomDialog id="pythonpath_Check" bind:dialog={pythonpathCheck} on:response={handlepythonPathCheck} title={"Python path is not valid"} content={"Change it in Settings --> Configuration"} label1="Okay" label2="Cancel" />

<Changelog  />

<section class="section animated fadeIn" id="Settings" style="display:none">

    <div class="columns">
        <div class="column side-panel is-2-widescreen is-3-desktop is-4-tablet box adjust-right">

            <div class="container left">
                <div class="title nav hvr-glow" class:clicked={selected==="Configuration"} on:click={navigate}>Configuration</div>
                <div class="title nav hvr-glow" class:clicked={selected==="Update"} on:click={navigate}>Update</div>
                <div class="title nav hvr-glow" class:clicked={selected==="Terminal"} on:click={navigate}>Terminal</div>
                <div class="title nav hvr-glow" class:clicked={selected==="About"} on:click={navigate}>About</div>

            </div>
        </div>

        <div class="column main-panel box">

            <div class="container right" id="Settings_right_column">

                <div class="content animated fadeIn" class:hide={selected!=="Configuration"}>
                    <h1 class="title">Configuration</h1>
                    <div class="subtitle">{$pyVersion}</div>

                    <button class="button is-link" on:click="{()=>$developerMode = !$developerMode}">Developer mode: {$developerMode} </button>
                    {#if $developerMode}
                         <!-- content here -->
                        <Textfield style="margin-bottom:1em;" bind:value={$pythonpath} label="Python path" />
                        <Textfield style="margin-bottom:1em;" bind:value={$pythonscript} label="Python script path" />
                        <button class="button is-link" on:click={resetPyConfig}>Reset</button>
                        <button class="button is-link" on:click={updatePyConfig}>Save</button>
                    {/if}
                </div>

                <div class="content animated fadeIn" class:hide={selected!=="Update"}>
                    <h1 class="title">Update</h1>

                    <div class="subtitle">Current Version {window.currentVersion}</div>
                    <div class="content">
                        <Textfield style="width:7em; margin-right:2em;" bind:value={$github.username} label="Github username" />
                        <Textfield style="width:7em; margin-right:2em;" bind:value={$github.repo} label="Github Repo" />
                        <CustomSelect bind:picked={$github.branch} label="Github branch" options={["master", "developer"]}/>
                    </div>

                    <div class="content">
                        <button class="button is-link" id="updateCheckBtn" on:click="{updateCheck}" on:update={update}>Check update</button>
                        <button class="button is-link" id="updateBtn" on:click={update}>Update</button>
                        
                        <button class="button is-warning" on:click="{()=>{$activateChangelog = true}}">What's New</button>
                    </div>


                    <div class="content">
                        <Textfield style="width:30%; margin-right:2em;" bind:value={$backupName} label="Github username" />
                        <button class="button is-link" on:click={backup}>Backup</button>
                        <button class="button is-link" on:click={restore}>Restore</button>
                    </div>
                    
                </div>

                <div class="content animated fadeIn" class:hide={selected!=="Terminal"}>
                    <h1 class="title">Terminal</h1>
                    <Terminal bind:commandToRun bind:commandArgsToRun id="Terminal-settings"/>
                </div>
                
                <div class="content animated fadeIn" class:hide={selected!=="About"}>
                    <h1 class="title">About</h1>

                </div>
                
            </div>
        </div>

    </div>
</section>