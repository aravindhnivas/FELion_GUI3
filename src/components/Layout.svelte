<script context="module">
    export function browse({filetype="", dir=true, multiple=true}={}) {
        return new Promise((resolve, reject)=>{
            const mainWindow = remote.getCurrentWindow()
            let type;
            dir ? type = "openDirectory" : type = "openFile"

            const options = {
                filters: [
                    { name: filetype, extensions: [`*${filetype}`] },
                    { name: 'All Files', extensions: ['*'] }
                ],

                properties: [type, multiple ? "multiSelections" : ""],
            }


            const version = parseInt(process.versions.electron.split(".")[0])

            
            if (version >= 7) {
                remote.dialog.showOpenDialog(mainWindow, options)
                .then(result => {
                    console.log(result.canceled)
                    console.log(result.filePaths)
                    resolve(result)

                }).catch(err => {

                    window.createToast("Couldn't open folder", "danger")
                    reject(err) })
            } else {
                let result = {}
                remote.dialog.showOpenDialog(null, options, location => {
                location === undefined ? result = {canceled:true, filePaths:[]}: result = {canceled:false, filePaths:location}

                console.log(result.canceled)
                console.log(result.filePaths)
                resolve(result)

            })
            }

        })
    }
</script>


<script>
    
    import { fly, fade } from 'svelte/transition';
    import Textfield from '@smui/textfield';
    import {onMount} from "svelte";
    import FileBrowser from "./FileBrowser.svelte"
    import { createEventDispatcher } from 'svelte';

    ////////////////////////////////////////////////////////////////////////////

    export let id, fileChecked=[], filetype = "felix", toggleBrowser = false, fullfileslist = [];
    export let currentLocation = db.get(`${filetype}_location`) || "", graphPlotted=false;

    // const dispatch = createEventDispatcher()
    // function tour_event() { dispatch('tour', {filetype}) }

    function browse_folder() {
        browse({dir:true}).then(result=>{

            console.log(result, currentLocation)
            if (!result.canceled) { 
                currentLocation = result.filePaths[0]
                db.set(`${filetype}_location`, currentLocation)
                console.log(result, currentLocation)
             }
        })
    }

    let mounted=false;
    
    onMount(()=>{ toggleBrowser = true; mounted=true;})

    let graphWindowClosed = true;
    $: graphModal = !graphWindowClosed
    let graphWindow;


    function openGraph(){

        if(!graphWindowClosed) {return graphWindow.show()}
        graphWindowClosed = false
        const mount = document.getElementById(`${filetype}-plotContainer`)

        graphWindow = new WinBox({
            root:document.getElementById("pageContainer"),

            mount,  title: `Modal: ${filetype}`,
            x: "center", y: "center",
            width: "70%", height: "70%",
            background:"#634e96",
            top: 50, bottom:50,
            onclose: function(){
                graphWindowClosed = true
                console.log(`${filetype}=> graphWindowClosed: ${graphWindowClosed}`)

                return false
            } 
        });

    }

</script>

<style lang="scss">

    .plot__div {padding: 1em;}
    .box {background-image: url(./assets/css/intro.svg); border-radius: 0;}

    .main__layout__div {
        display: grid;
        grid-auto-flow: column;
        width: 100%;
        height: calc(100vh - 6rem);
        grid-template-columns: auto 1fr;
        column-gap: 3em;
        .left_container__div { max-width: 100%; }

        .right_container__div {

            display: grid;
            row-gap: 1em;
        
            grid-template-rows: auto auto 1fr;
            max-height: calc(100vh - 7rem);

        
            .location__div {
                display:grid;
                grid-template-columns: auto 1fr;
                column-gap: 1em;
        
                align-items: baseline;
            }
        

            .plot__div {
        
                display: flex;
                row-gap: 1em;

                flex-direction: column;
                overflow: auto;
                padding-right: 1em;
            }
        }
    }

</style>

<section {id} style="display:none" class="animated fadeIn">
    <div class="main__layout__div">

        <div class="left_container__div box " transition:fly="{{ x: -100, duration: 500 }}">
            <FileBrowser bind:currentLocation {filetype} bind:fileChecked on:chdir bind:fullfileslist/>
        </div>

        <div class="right_container__div box " id="{filetype}__mainContainer__div" >

            <div class="location__div" >
                <button class="button is-link" id="{filetype}_filebrowser_btn" on:click={browse_folder}>Browse</button>
                <Textfield bind:value={currentLocation} label="Current location" style="width:100%; "/>
            </div>

            <div class="button__div align" id="{filetype}-buttonContainer" >
                <slot name="buttonContainer" />
                {#if graphPlotted}

                    <button class="button is-warning animated fadeIn" on:click={openGraph}>Graph:Open separately</button>
                {/if}
            </div>

            <div class="plot__div" id="{filetype}-plotContainer" transition:fade> 
                <slot name="plotContainer" />
                {#if graphPlotted}
                    <slot name="plotContainer_functions" />

                    <slot name="plotContainer_reports" />
                {/if}
            </div>
        </div>
    </div>

</section>