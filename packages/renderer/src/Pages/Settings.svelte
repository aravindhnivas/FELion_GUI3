<script>
    
    import {
        pyVersion,
        pythonpath,
        pythonscript,
        pyServerPORT,
        developerMode,
        pyServerReady,
    }                               from "./settings/svelteWritables";

    import {activateChangelog}      from "../js/functions"

    import {
        getPyVersion,
        resetPyConfig, 
        updatePyConfig,
    }                               from "./settings/checkPython";
    
    import Textfield                from '@smui/textfield';
    import {onMount, onDestroy}     from "svelte";
    import Changelog                from "$components/Changelog.svelte";
    import PyButton                 from "$components/PyButton.svelte"
    import computefromSubprocess    from "$src/Pages/general/computefromSubprocess"
    import CustomSwitch             from '$components/CustomSwitch.svelte';
    
    import {
        checkTCP,
        isportOpen,
        isItfelionpy,
        closeConnection,
        fetchServerROOT,
    } from "./settings/serverConnections"

    
    const navigate = (e) => {selected = e.target.innerHTML; window.db.set("settingsActiveTab", selected);}
    let selected = window.db.get("settingsActiveTab") || "Update"
    let mounted = false

    let updateInterval;
    let pyError = "", updateError=""
    
    onMount(async ()=>{
        try {
            await getPyVersion()
        } 
        catch (error) {pyError = error;}
        finally {

            startpythonServer()
            mounted = true
            if(env.DEV) return
            const interval = 15 //min
            updateInterval = setInterval(() => {
                updateCheck()
                updateError = localStorage.getItem("update-error")
            }, interval*60*1000);
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
    let serverDebug = false;
    let pythonServer = [];

    let serverInfo = ""
    let executeCommand = ""

    const closeOpenPort = async () => {
        const PID = await isportOpen()
        if(PID) {

            if(await isItfelionpy()) {
                const infoMessage = `felionpy connection already opened on port ${$pyServerPORT}`
                serverInfo += ">> Info: "+infoMessage+"\n"
                serverInfo += `>> pid: ${PID} closing felionpy previous connection\n`

                const status = await closeConnection(PID)
                serverInfo += `>> ${status}\n`
                
                return Promise.resolve()
            } else {
                const warnningMessage = `port: ${$pyServerPORT} is not free and already in use by other program`
                serverInfo += ">> Warning: "+warnningMessage+"\n"
                return Promise.reject(warnningMessage)

            }

        }
    }

    const startpythonServer = async (e) => {
        try {
            await closeOpenPort()
            serverInfo += ">> Establishing python server connection \n"
            const pythonServerButton = document.getElementById("pythonServerButton")
            await computefromSubprocess({
                button: e?.target || pythonServerButton,
                general: true, 
                pyfile: "server",
                args: {
                    port: $pyServerPORT,
                    debug: serverDebug
                }

            })
            await updateTCPInfo()
        } catch (error) {window.handleError(error)}
    }

    $: if($pyServerReady) {
        updateServerInfo()
        updateTCPInfo()
    }

    $: if($pyServerPORT) {db.set("pyServerPORT", $pyServerPORT)}

    const updateServerInfo = async ()=>{
        const rootpage = await fetchServerROOT()
        if(rootpage) { serverInfo += `>> ${rootpage}\n` }
    }

    const updateTCPInfo = async ()=>{
        const [{stdout}] = await checkTCP()
        if(stdout) { serverInfo += `>> ${stdout}\n` }
    }

    onDestroy(() => {
        $pyServerReady = false
        if(updateInterval) {
            console.warn("Clearing update interval")
            clearInterval(updateInterval)
        }
    });

</script>

<Changelog  />

<section class="section animated fadeIn" id="Settings" style="display:none">

    <div class="main__div">
        
        <div class="box interact left_container__div">
           <div class="title__div">

                <div class="hvr-glow" class:clicked={selected==="Configuration"} on:click={navigate}>Configuration</div>
                <div class="hvr-glow" class:clicked={selected==="Update"} on:click={navigate}>Update</div>
                <div class="hvr-glow" class:clicked={selected==="About"} on:click={navigate}>About</div>

           </div>
        </div>

        <div class="box">

            <div class="container right" id="Settings_right_column">

                <div class="align animated fadeIn" class:hide={selected!=="Configuration"}>

                    <h1>Configuration</h1>
                    
                    <div class="align">
                    
                        <div class="tag is-warning">{$pyVersion || "Python undefined"}</div>

                        <div class="align">

                            <button class="button is-link" on:click="{()=> {$developerMode = !$developerMode; window.db.set("developerMode", $developerMode)}}">Developer mode: {$developerMode} </button>
                            <button class="button is-link" on:click="{getPyVersion}">getPyVersion </button>
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

                        
                        <div class="align">

                            <Textfield bind:value={$pyServerPORT} label="serverPORT" />
                            <CustomSwitch bind:selected={serverDebug} label="serverDebug" />

                            <PyButton id="pythonServerButton" on:click={startpythonServer} 
                                    bind:pyProcesses={pythonServer}
                                    disabled={pythonServer.length>0}
                                    btnName={"startpythonServer"}
                            />
                            {#if pythonServer.length>0}
                                <button class="button is-danger" on:click="{()=>{
                                    const currentServer = pythonServer[0]
                                    currentServer.kill()
                                    console.log(currentServer)
                                }}">
                                    STOP
                                </button>
                            {/if}

                            <button class="button is-warning" on:click="{updateTCPInfo}">Check TCP</button>

                        </div>


                        <div class="align">
                            <Textfield bind:value={executeCommand} label="executeCommands" />
                            <button class="button is-link" on:click="{async ()=>{
                                const [{stdout}] = await exec(executeCommand)
                                serverInfo += `>> ${stdout}\n`
                            }}">executeCommand</button>
                            <button id="fetchServerROOT" class="button is-link" on:click="{updateServerInfo}">fetchServerROOT</button>
                            <button class="button is-danger" on:click="{()=>{serverInfo = ""}}">Clear</button>

                        </div>

                        <div class="align box" style="white-space: pre-wrap; user-select: text;">
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

    .right {
        div {
            overflow-y: auto;
            max-height: calc(84vh - 2rem);
            padding-right: 1em;
        }
    }
    
</style>
