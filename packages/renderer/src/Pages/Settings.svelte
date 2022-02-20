<script>
    import {
        pyVersion,
        pythonpath,
        pythonscript,
        developerMode, pyProgram,
        suppressInitialDeveloperWarning
    }                               from "./settings/svelteWritables";
    import {activateChangelog}      from "../js/functions"
    import {
        resetPyConfig, updatePyConfig
    }                               from "./settings/checkPython";

    import Textfield                from '@smui/textfield';
    import {onMount, onDestroy}     from "svelte";
    import CustomSwitch             from '$components/CustomSwitch.svelte';
    import Changelog                from "$components/Changelog.svelte";
    import Terminal                 from '$components/Terminal.svelte';
    import {mainPreModal}           from "$src/svelteWritable";
    
    let selected = window.db.get("settingsActiveTab") || "Update"
    const navigate = (e) => {selected = e.target.innerHTML; window.db.set("settingsActiveTab", selected);}

    let updateInterval;
    onMount(async ()=>{
        await getPyVersion()
        // Update check
        if(env.DEV) return
        const interval = 15 //min
        updateInterval = setInterval(() => {
            updateCheck()
            updateError = localStorage.getItem("update-error")
        }, interval*60*1000);
    })
    onDestroy(() => env.DEV ? "" : clearInterval(updateInterval));
    
    let pyError = "", updateError=""
    const getPyVersion = async (e) => {
        e?.target?.classList.toggle("is-loading")
        const pyfile = "getVersion"
        const pyArgs = $developerMode ? pathJoin($pythonscript, "main.py") : ""
        const command = `${$pyProgram} ${pyArgs} ${pyfile} {} `
        const [{stdout}, error] = await exec(command)
        const [version] = stdout?.split("\n").filter?.(line => line.includes("Python")) || [""]

        $pyVersion = version?.trim() || ""
        console.log({stdout, version})
        pyError = error;
        e?.target?.classList.toggle("is-loading")
    }

    let commandToRun = "", commandArgsToRun = "";

    function updateCheck(event=null){

        
        if(env.DEV) return console.info("Cannot update in DEV mode")

        try {
            event?.target.classList.toggle("is-loading")
        
            if (!navigator.onLine) {if (info) {window.createToast("No Internet Connection!", "warning")}; return}
            checkupdate()
        } catch (error) {
        
            if(event) window.handleError(error)
        } finally {
            event?.target.classList.toggle("is-loading")
        }
    }
</script>

<Changelog  />

<section class="section animated fadeIn" id="Settings" style="display:none">
    <div class="main__div">
        
        <div class="box interact left_container__div">

           <div class="title__div">
                <div class="hvr-glow" class:clicked={selected==="Configuration"} on:click={navigate}>Configuration</div>
                <div class="hvr-glow" class:clicked={selected==="Update"} on:click={navigate}>Update</div>
                <div class="hvr-glow" class:clicked={selected==="Terminal"} on:click={navigate}>Terminal</div>
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
                                <div class="align">
                                    <CustomSwitch on:SMUISwitch:change={()=>window.db.set("suppressInitialDeveloperWarning", $suppressInitialDeveloperWarning)} bind:selected={$suppressInitialDeveloperWarning} label="suppressWarning"/>
                                </div>
                            {/if}

                            {#if pyError}
                                <div class="tag is-danger errorbox">{pyError}</div>
                            {/if}

                        </div>


                        {#if window.env.DEV}
                            <button class="button is-link" style="margin: 1em;" on:click={()=>{
                                const string = "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque laboriosam vitae officia deleniti corporis aliquid quo id. Laboriosam officia hic nam nemo fuga eum. Veritatis voluptatem ipsa odit incidunt, velit quidem fuga! Minima provident officiis iste magnam at magni suscipit iusto vel fugiat aliquam explicabo ad qui, ipsum vero perspiciatis, facere est eius ullam omnis maiores? Fugit aut saepe accusantium deserunt eligendi corporis in et. Deleniti natus rerum voluptates fuga consequatur qui tempore omnis optio illum soluta odio perferendis doloribus repudiandae vero non, commodi recusandae reiciendis laboriosam neque et dolore quos reprehenderit consectetur laborum? Aperiam, laboriosam id! Culpa, iusto quisquam."
                                mainPreModal.error(string+string)
                            }}>Throw error</button>
                        {/if}
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

                <div class="animated fadeIn" class:hide={selected!=="Terminal"}>
                    <h1 class="title">Terminal</h1>
                    <Terminal bind:commandToRun bind:commandArgsToRun id="Terminal-settings"/>
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

    h1, h2 {
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
    
</style>

