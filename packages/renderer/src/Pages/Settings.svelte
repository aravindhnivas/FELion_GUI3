<script>
    
    import {
        pyVersion,
        pythonpath,
        pythonscript,
        pyServerPORT,
        developerMode,
        pyServerReady,
    }                               from "./settings/svelteWritables";
    import {updateInterval}         from "$src/svelteWritable";
    import {activateChangelog}      from "../js/functions"

    import {
        getPyVersion,
        resetPyConfig, 
        updatePyConfig,
    }                               from "./settings/checkPython";
    import Textfield                from '@smui/textfield';
    import {onMount, onDestroy}     from "svelte";
    import Changelog                from "$components/Changelog.svelte";

    import CustomSwitch             from '$components/CustomSwitch.svelte';
    import {
        checkTCP,
        fetchServerROOT,
    } from "./settings/serverConnections"
    
    let pyError = ""
    let mounted = false
    let updateError=db.get("updateError") || ""
    let updateIntervalCycle;
    let selected = window.db.get("settingsActiveTab") || "Configuration"
    
    const navigate = (e) => {selected = e.target.innerHTML; window.db.set("settingsActiveTab", selected);}
    db.onDidChange("pyServerReady", async (value)=>{
        $pyServerReady = value
        if($pyServerReady) {
            serverInfo += `>> fetching server status\n`
            await updateServerInfo()
        }
    })

    db.onDidChange("updateError", (err)=>{updateError = err})

    db.onDidChange("delayupdate", (delay)=>{
        if(delay) {
            if(updateIntervalCycle) {clearInterval(updateIntervalCycle)}

            setTimeout(()=>{
                updateCheck()
                updateIntervalCycle = setInterval(updateCheck, $updateInterval*60*1000);

            }, 60*60*1000)
        }

    })
    
    onMount(async ()=>{

        try {
            if(!$pyVersion) {
                console.warn("python is invalid. computing again")
                await getPyVersion()
                console.warn($pyVersion)
            }

            $pyServerReady = db.get("pyServerReady")
        } 
        catch (error) {pyError = error}
        finally {
            mounted = true
            serverInfo += `>> pyVersion: ${$pyVersion}\n`
            if($pyServerReady) {await updateServerInfo()}
            if(env.DEV) return
        
            updateIntervalCycle = setInterval(updateCheck, $updateInterval*60*1000);
        }

    })

    function updateCheck(event=null){
        if(env.DEV) return console.info("Cannot update in DEV mode")

        try {
            event?.target.classList.toggle("is-loading")
            if (!navigator.onLine) {if (event) {return window.createToast("No Internet Connection!", "warning")}}
            checkupdate()
        } catch (error) { if(event) window.handleError(error)
        } finally {event?.target.classList.toggle("is-loading")}
    }

    let serverInfo = ""

    const updateServerInfo = async (e=null)=>{
        const rootpage = await fetchServerROOT({target: e?.target})
        if(!rootpage.includes("ERROR")) { 
            $pyServerReady = true
            serverInfo += `>> ${rootpage}\n`; 
            return
        }
    }

    let serverDebug = db.get("serverDebug") || false
    const updateTCPInfo = async (e=null)=>{
        const [{stdout}] = await checkTCP({target: e?.target})
        if(stdout) { serverInfo += `>> ${stdout}\n` }
        else {serverInfo += `>> ERROR occured while checking TCP connection on port:${$pyServerPORT}\n`}
    }
    
    let showServerControls = false
    onDestroy(() => {if(updateIntervalCycle) { clearInterval(updateIntervalCycle) }})

    const id="Settings"
    let display = db.get("active_tab") === id ? 'block' : 'none'

</script>

<Changelog  />

<section class="section animated fadeIn" {id} style="display:{display}">

    <div class="main__div">
        
        <div class="box interact left_container__div">
           <div class="title__div">
                <div class="hvr-glow" class:clicked={selected==="Configuration"} on:click={navigate}>Configuration</div>
                <div class="hvr-glow" class:clicked={selected==="Update"} on:click={navigate}>Update</div>
                <div class="hvr-glow" class:clicked={selected==="About"} on:click={navigate}>About</div>
           </div>
        </div>

        <div class="mainContainer box">

            <div class="container right" id="Settings_right_column">

                <div class="align animated fadeIn" class:hide={selected!=="Configuration"}>

                    <h1>Configuration</h1>
                    
                    <div class="align">
                    
                        <div class="tag is-warning">{$pyVersion || "Python undefined"}</div>
                        <div class="tag" 
                            class:is-danger={!$pyServerReady}
                            class:is-success={$pyServerReady}
                        >{$pyServerReady ? `server running (port: ${$pyServerPORT})` : "felionpy server closed"}</div>

                        <div class="align">

                            <button class="button is-link" on:click="{
                                    ()=> {
                                        $developerMode = !$developerMode;
                                        window.db.set("developerMode", $developerMode)
                                    }
                                }">
                                Developer mode: {$developerMode}
                            
                            </button>

                            <button class="button is-link" on:click="{getPyVersion}">getPyVersion</button>
                            
                            <button class="button is-link" 
                                on:click="{()=>showServerControls=!showServerControls}"
                                >
                                Show server controls
                            </button>
                            
                            {#if $developerMode}

                                <div class="align">
                                    <Textfield bind:value={$pythonpath} label="Python path" style="width: 100%; "/>
                                    <Textfield bind:value={$pythonscript} label="Python script path" style="width: 100%; " />
                                    <button class="button is-link" on:click={resetPyConfig}>Reset</button>
                                    <button class="button is-link" on:click={updatePyConfig}>Save</button>
                                </div>

                            {/if}
                        </div>

                        {#if pyError}
                            <div class="align tag is-danger errorbox">{pyError}</div>

                        {/if}

                        
                        <div class="align server-control" class:hide={!showServerControls}>
                            <div class="align">

                                <Textfield disabled type="number" bind:value={$pyServerPORT} label="serverPORT" />
                                
                                <CustomSwitch bind:selected={serverDebug} label="serverDebug" 
                                    on:SMUISwitch:change="{()=>{
                                        db.set("serverDebug", serverDebug);
                                        console.log({serverDebug}, db.get("serverDebug"))
                                    }}"
                                />

                                <button class="button is-link" on:click="{window.startServer}" 
                                    disabled={$pyServerReady}
                                    >
                                    STARTserver
                                </button>
                                
                                {#if $pyServerReady}
                                    <button class="button is-danger" on:click="{window.stopServer}">
                                        STOPserver
                                    </button>
                                {/if}
    
                                <button class="button is-warning" on:click="{updateTCPInfo}">Check TCP</button>
    
                            </div>
    
    
                            <div class="align">
                                <button id="fetchServerROOT" class="button is-link" on:click="{updateServerInfo}">fetchServerROOT</button>
                                <button class="button is-danger" on:click="{()=>{serverInfo = ""}}">Clear</button>
                            </div>

                        </div>

                        <div class="serverContainer align box">
                            {serverInfo}
                        </div>

                    </div>
                    
                </div>

                <div class="align animated fadeIn" class:hide={selected!=="Update"}>
                    <h1 class="title">Update</h1>

                    <div class="subtitle" style="width: 100%;"  >App Version {window.appVersion}</div>
                    <div class="align">
                    
                        <div class="align">
                            <button class="button is-link" id="updateCheckBtn" on:click="{updateCheck}" >Check update</button>
                            <button class="button is-warning" on:click="{()=>{$activateChangelog = true}}">What's New</button>
                        </div>


                        <div id="update-progress-container" style="display: none;">
                            <label for="file">Download progress:</label>
                            <progress id="update-progress" max="100" value="0"> 0%</progress>
                        </div>


                        {#if updateError}
                            <div class="tag is-danger errorbox">{updateError}</div>
                        {/if}

                    </div>
                </div>

                <div class="animated fadeIn" class:hide={selected!=="About"}>
                    <h1 class="title">About</h1>
                    <div class="content">
                    
                        <ul style="user-select: text;">
                            <li>FELionGUI: {window.appVersion}</li>
                            <li>{$pyVersion}</li>
                            <hr>
                            {#each Object.keys(window.versions) as key}
                                <li>{key}: {window.versions[key]}</li>
                            {/each}
                    
                        </ul>
                    </div>
                </div>

            </div>
        </div>
    
    </div>

</section>

<style lang="scss">
    
    section { margin: 0; padding: 0; }
    .clicked {border-bottom: solid 1px; }
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
            div {font-size: 22px; }
        } 

        #update-progress-container {
            progress {width: 100%;}
            display: grid;
            width: 100%;
            gap: 1em;
            grid-template-columns: auto 1fr;
            align-items: center;
        }
    }

    h1 {

        margin: 0;
        width: 100%;
    }

    .errorbox {
        white-space: pre-line;
        height: 100%;
        width: fit-content;

        font-size: medium;
        margin-left: auto;
        border: solid 1px;

    }
    

    .mainContainer {overflow: auto;}

    .serverContainer {
        overflow: auto;
        user-select: text;
        white-space: pre-wrap;
        align-items: baseline;
        height: calc(42vh - 5rem);
        max-height: calc(42vh - 5rem);
    }

</style>
