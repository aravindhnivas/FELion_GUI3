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
    import Hamburger1 from "../components/icon_animations/Hamburger1.svelte";
    import { createEventDispatcher } from 'svelte';

    ////////////////////////////////////////////////////////////////////////////

    export let id, fileChecked=[], filetype = "felix", toggleBrowser = false, fullfileslist = [];
    export let currentLocation = db.get(`${filetype}_location`) || "", graphPlotted=false;

    const dispatch = createEventDispatcher()


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

    
    function tour_event() { dispatch('tour', {filetype}) }

    let ContainerHeight, buttonContainerHeight, mounted=false;
    
    
    onMount(()=>{ toggleBrowser = true; mounted=true;})

    let graphWindowClosed = true;
    $: graphModal = !graphWindowClosed

    const plotContainer = document.getElementById(`${filetype}-plotContainer`)
    $: plotContainerStyle = graphModal ? "padding: 1em;" : `max-height: calc(100vh - 20em); height:calc(${ContainerHeight}px - ${buttonContainerHeight}px - 11em)`
    let graphWindow;

    function openGraph(){

        if(!graphWindowClosed) {
            return graphWindow.show()
        }
        graphWindowClosed = false

        const mount = document.getElementById(`${filetype}-plotContainer`)

        graphWindow = new WinBox({
            root:document.getElementById("pageContainer"), 
            mount, 

            title: `Modal: ${filetype}`,

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


    // Small tablets (portrait view)
    $screen-tablet: 770px;
    @mixin tablet {

        @media (min-width: #{$screen-tablet}) {
            @content;
        
        }
    }

    // Small desktops
    $screen-sm: 1024px;

    @mixin sm {
        @media (min-width: #{$screen-sm}) {
        
            @content;
        }
    }

    // Medium desktops
    $screen-md: 1440px;

    @mixin md {
        
        @media (min-width: #{$screen-md}) {
        
            @content;
        
        }
    }

    // Large desktops
    $screen-lg: 1920px;

    @mixin lg {
        @media (min-width: #{$screen-lg}) {
        
            @content;
        
        }
    }

    $box1: #6a50ad59;
    .filebrowser, .fileContainer {
        background-image: url(./assets/css/intro.svg);
        height: calc(100vh - 7em);
    }

    .plotContainer {
        overflow-y: auto; padding-bottom: 12em;  padding-right: 1em;
        div {margin-top: 1em;}
    }
     
    .filebrowser {

        padding-left: 2em;
        padding-top: 1em;
        background-color: $box1;

        border-radius: 0;
    }
    
    .fileContainer {

        margin: 0 2em; padding-bottom: 5rem; width: auto;
        @include tablet { width: 60%; }
    }

    .buttonContainer { max-height: 20em; overflow-y: auto; }
    .box {border-radius: 0;}
    .container {height: calc(100vh - 7em);}
    .location__bar {
        display:grid;
        grid-auto-flow: column;
        grid-template-columns: auto auto 1fr;
        grid-column-gap: 1em;
        align-items: baseline;
        margin-bottom: 1em;
    
    }

    .buttonContainer {
        display: grid;

        grid-auto-flow: row;
        align-items: center;
    }

</style>


<section {id} style="display:none" class="animated fadeIn">
    <div class="columns">

        {#if toggleBrowser}
            <div class="column is-one-fifth-widescreen is-one-quarter-desktop box filebrowser adjust-right" transition:fly="{{ x: -100, duration: 500 }}">
                <FileBrowser bind:currentLocation {filetype} bind:fileChecked on:chdir bind:fullfileslist/>

            </div>
        {/if}

        <div class="column fileContainer" >

            <div class="container button-plot-container box" id="{filetype}-button-plot-container" bind:clientHeight={ContainerHeight}>
                <div class="location__bar" >
                    <Hamburger1 bind:active={toggleBrowser}/>

                    <button class="button is-link" id="{filetype}_filebrowser_btn" on:click={browse_folder}>Browse</button>
                    <Textfield bind:value={currentLocation} label="Current location" style="width:100%; "/>
                </div>

                <div class="buttonContainer" id="{filetype}-buttonContainer" bind:clientHeight={buttonContainerHeight}>
                    {#if toggleBrowser}
                        <slot name="buttonContainer" />
                        {#if graphPlotted}
                            <button class="button is-warning animated fadeIn" style="width:12em;" on:click={openGraph}>Graph:Open separately</button>
                        {/if}
                    {/if}
                 </div>

                <div class="plotContainer" id="{filetype}-plotContainer" style="{plotContainerStyle}" transition:fade> 

                    <slot name="plotContainer" />
                    {#if graphPlotted}
                        <slot name="plotContainer_functions" />
                        <slot name="plotContainer_reports" />
                    {/if}
                </div>

            </div>
        </div>
    </div>
    
</section>