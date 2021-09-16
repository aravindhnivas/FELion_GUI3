<script>

    // Importing modules
    import {pythonpath, pythonscript, pyVersion, github, backupName, developerMode, suppressInitialDeveloperWarning} from "./settings/svelteWritables";
    import {mainPreModal} from "../svelteWritable";
    import {activateChangelog, windowLoaded} from "../js/functions"
    import Textfield from '@smui/textfield';
    import {onMount} from "svelte";
    import CustomDialog from "../components/CustomDialog.svelte"
    import CustomSelect from '../components/CustomSelect.svelte';
    import CustomSwitch from '../components/CustomSwitch.svelte';
    import Changelog from "../components/Changelog.svelte";

    import {download} from "./settings/donwloadUpdate";
    
    import {InstallUpdate} from "./settings/installUpdate";
    
    // import { Button, Message, Snackbar } from 'svelma'

    
    import {updateCheck} from "./settings/updateCheck";
    import {resetPyConfig, updatePyConfig} from "./settings/checkPython";
    import {backupRestore} from "./settings/backupAndRestore";
    import {tick} from "svelte";
    import Terminal from '../components/Terminal.svelte';

    const backup = (event) => {
        backupRestore({event, method:"backup"})
            .then(()=>console.log("Backup Completed"))
            .catch((error)=>{mainPreModal.error(error.stack || error)})
    }

    const restore = (event) => {
        backupRestore({event, method:"restore"})
        .then(()=>console.log("Restore Completed"))
        .catch((error)=>{mainPreModal.error(error.stack || error)})

    }

    let selected = db.get("settingsActiveTab") || "Update"
    
    const navigate = (e) => {selected = e.target.innerHTML; db.set("settingsActiveTab", selected);}


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
            const updateFolder = pathResolve(__dirname, "..", "update")
            let target = document.getElementById("updateBtn")
            target.classList.toggle("is-loading")
            if (!existsSync(updateFolder)) {mkdirSync(updateFolder)}
            await download(updateFolder)
            InstallUpdate(target, updateFolder)
        } catch (error) {mainPreModal.error(error.stack || error)}
        
    }

    let commandToRun = "", commandArgsToRun = "";
    
    // $: if($developerMode&&$windowLoaded&&!$suppressInitialDeveloperWarning) {window.showStackContext({title:"Warning", text:"If python path is invalid, the program might not work", type:"error"});}

    // $: if($github.branch === "developer") {
    //     window.showStackContext({title:"Warning", text:"Developer channel may not be stable and contains bugs.", type:"error"});

    // }

</script>

<style lang="scss">

    section { margin: 0; padding: 0; }
    .clicked {border-left: 2px solid #fafafa; border: solid 1px; border-radius: 1em;}

    * :global(option) { color: black; }
    .main__div {
        display: grid;
        grid-template-columns: 1fr 4fr;
        column-gap: 3em;
        height: calc(100vh - 7rem);
        .box {

            margin-bottom: 0px;
            border-radius: 0;

            background-color: #6a50ad8a;

        }
        .title__div{
            letter-spacing: 0.1em;
            text-transform: uppercase;
            text-align: center;
            cursor: pointer;
            display: grid;
            row-gap: 2em;

            div {font-size: 25px; border-radius: 1em;}
        } 

    }



</style>

<CustomDialog id="pythonpath_Check" bind:dialog={pythonpathCheck} on:response={handlepythonPathCheck} title={"Python path is not valid"} content={"Change it in Settings --> Configuration"} label1="Okay" label2="Cancel" />
<Changelog  />

<section class="section animated fadeIn" id="Settings" style="display:none">
    <div class="main__div">
        <div class="box left_container__div">

           <div class="title__div">
                <div class="hvr-glow" class:clicked={selected==="Configuration"} on:click={navigate}>Configuration</div>
                <div class="hvr-glow" class:clicked={selected==="Update"} on:click={navigate}>Update</div>
                <div class="hvr-glow" class:clicked={selected==="Terminal"} on:click={navigate}>Terminal</div>

                <div class="hvr-glow" class:clicked={selected==="About"} on:click={navigate}>About</div>
           </div>
        </div>

        <div class="box">
            <div class="container right" id="Settings_right_column">
                <div class="content animated fadeIn" class:hide={selected!=="Configuration"}>
                    <h1 class="title">Configuration</h1>

                    <div class="subtitle">{$pyVersion}</div>

                    <div class="align">
                        <button class="button is-link" on:click="{()=>$developerMode = !$developerMode}">Developer mode: {$developerMode} </button>
                        {#if $developerMode}

                            <div class="align">
                                <Textfield bind:value={$pythonpath} label="Python path" style="width: 100%; "/>
                                <Textfield bind:value={$pythonscript} label="Python script path" style="width: 100%; " />
                                <button class="button is-link" on:click={resetPyConfig}>Reset</button>
        
                                <button class="button is-link" on:click={updatePyConfig}>Save</button>
                            </div>
                            <div class="align">
                                <CustomSwitch on:change={()=>db.set("suppressInitialDeveloperWarning", $suppressInitialDeveloperWarning)} bind:selected={$suppressInitialDeveloperWarning} label="suppressWarning"/>
                            </div>
                        {/if}
                    </div>
                </div>

                <div class="content animated fadeIn" class:hide={selected!=="Update"}>
                    <h1 class="title">Update</h1>

                    <div class="subtitle">Current Version {window.currentVersion}</div>
                    <div class="align">
                    
                        <div class="align">
                            <Textfield  bind:value={$github.username} label="Github username" />
                            <Textfield  bind:value={$github.repo} label="Github Repo" />
                            <CustomSelect bind:picked={$github.branch} label="Github branch" options={["master", "developer"]}/>
                        </div>

                        <div class="align">
                            <button class="button is-link" id="updateCheckBtn" on:click="{updateCheck}" on:update={update}>Check update</button>
                            <button class="button is-link" id="updateBtn" on:click={update}>Update</button>
                            
                            <button class="button is-warning" on:click="{()=>{$activateChangelog = true}}">What's New</button>
                        </div>


                        <div class="align">
                            <Textfield  bind:value={$backupName} label="Github username" />
                            <button class="button is-link" on:click={backup}>Backup</button>
                            <button class="button is-link" on:click={restore}>Restore</button>
                        </div>
                    </div>
                    
                </div>

                <div class="animated fadeIn" class:hide={selected!=="Terminal"}>
                    <h1 class="title">Terminal</h1>
                    <Terminal bind:commandToRun bind:commandArgsToRun id="Terminal-settings"/>
                </div>
                
                <div class="align animated fadeIn" class:hide={selected!=="About"}>
                    <h1 class="title">About</h1>

                </div>
                
            </div>
        
        </div>

    </div>

</section>