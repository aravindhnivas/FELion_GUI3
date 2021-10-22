<script context="module">
    export async function browse({filetype="", dir=true, multiple=true}={}) {
        let type;
        dir ? type = "openDirectory" : type = "openFile"
        const options = {
            filters: [
                { name: filetype, extensions: [`*${filetype}`] },
                { name: 'All Files', extensions: ['*'] }
            ],
            properties: [type, multiple ? "multiSelections" : ""],
        }
        const {showOpenDialogSync} = dialogs

        const result = await showOpenDialogSync(options)
        return result
    }
</script>


<script>
    
    import { fly, fade } from 'svelte/transition';
    import Textfield from '@smui/textfield';
    import {onMount, tick} from "svelte";
    import FileBrowser from "./FileBrowser.svelte"
    import Modal from "./Modal.svelte"
    import { createEventDispatcher } from 'svelte';
    import IconButton from '@smui/icon-button';
    
    ////////////////////////////////////////////////////////////////////////////

    export let id, fileChecked=[], filetype = "felix", toggleBrowser = false, fullfileslist = [];
    export let currentLocation = db.get(`${filetype}_location`) || "", graphPlotted=false;
    export let graphWindowClasses = ["no-full"]
    export let activateConfigModal = false
    const dispatch = createEventDispatcher()

    function browse_folder() {

        browse({dir:true}).then(result=>{
            if (result) { 
                currentLocation = result[0]
                db.set(`${filetype}_location`, currentLocation)
                console.log(result, currentLocation)                
            }
        })
    }

    let mounted=false;
    let graphDivs = []
    onMount(()=>{ toggleBrowser = true; mounted=true; })

    const lookForGraph = () => {
        try {graphDivs = Array.from(document.querySelectorAll(`#${filetype}-plotContainer .graph__div`)) } 
        catch (error) {console.log(error)}
    }

    function openGraph(){
        const mount = document.getElementById(`${filetype}-plotContainer`)
        const graphWindow = new WinBox({ class: graphWindowClasses,
            root:document.getElementById("pageContainer"),
            mount,  title: `Modal: ${filetype}`,
            x: "center", y: "center",
            width: "70%", height: "70%",
            background:"#634e96",
            top: 50, bottom:50,

            onclose: async function(){
                changeGraphDivWidth()
                return false
            },
            onresize: function(width, height){changeGraphDivWidth()},
            onfocus: ()=>{changeGraphDivWidth()}
        });
        graphWindow.maximize(true);
        
    }

    let plotWidth;
    const changeGraphDivWidth = async () => {

        await tick(); 
        graphDivs.forEach(id=>{
            if(id.data) {Plotly.relayout(id, {width:id.clientWidth})}
        })
    }

    $: if (plotWidth && mouseReleased) {changeGraphDivWidth()};
    let mouseReleased = true;

</script>


<style lang="scss">
    // .plot__div {padding: 1em;}
    .box {background-image: url(./assets/css/intro.svg); border-radius: 0;}
    .main__layout__div {
        display: grid;
        grid-auto-flow: column;
        width: 100%;

        height: calc(100vh - 6rem);
        grid-template-columns: auto 1fr;
        column-gap: 3em;

        .left_container__div { max-width: 100%; margin-bottom: 0;}
        .right_container__div {
            display: grid;
            row-gap: 1em;

            grid-template-rows: auto auto 1fr;
            max-height: calc(100vh - 6rem);
            .location__div {
                display:grid;
                grid-template-columns: auto 1fr auto;
                column-gap: 1em;
                align-items: baseline;
            }

        }
    }
    .plot__div {
        display: flex;
        row-gap: 1em;
        flex-direction: column;
        overflow: auto;
        padding-right: 1em;
        padding-bottom: 12em;
    }
</style>

<section {id} style="display:none" class="animated fadeIn">

    <div class="main__layout__div">
        <div class="interact left_container__div box " transition:fly="{{ x: -100, duration: 500 }}" on:mouseup={()=>mouseReleased=true} on:mousedown={()=>mouseReleased=false} >

            <FileBrowser bind:currentLocation {filetype} bind:fileChecked on:chdir bind:fullfileslist on:markedFile/>
        </div>

        <div class="right_container__div box " id="{filetype}__mainContainer__div" >

            <div class="location__div" >
                <button class="button is-link" id="{filetype}_filebrowser_btn" on:click={browse_folder}>Browse</button>

                <Textfield bind:value={currentLocation} label="Current location" style="width:100%; "/>
                <IconButton class="material-icons" on:click={() => activateConfigModal=true} >build</IconButton>
            </div>

            <div class="button__div align" id="{filetype}-buttonContainer" >
                <slot name="buttonContainer" />

                {#if graphPlotted}
                    <button class="button is-warning animated fadeIn" on:click={openGraph}>Graph:Open separately</button>

                {/if}

            </div>

            <div class="plot__div" id="{filetype}-plotContainer" transition:fade use:lookForGraph bind:clientWidth={plotWidth}> 

                <slot name="plotContainer" {lookForGraph} />
                {#if graphPlotted}
                    <slot name="plotContainer_functions" />
                    <slot name="plotContainer_reports" />
                {/if}
            </div>

        </div>

        {#if activateConfigModal}
            <Modal title="{filetype.toUpperCase()} Settings" bind:active={activateConfigModal} >
                <svelte:fragment slot="content">
                    <slot name="config"></slot>
                </svelte:fragment>
                <svelte:fragment slot="footerbtn">
                    <button class="button is-link" on:click={()=>{dispatch('configSave', {filetype})}}>Save</button>
                </svelte:fragment>

            </Modal>
        {/if}
    </div>

    
</section>