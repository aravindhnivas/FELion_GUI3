<script context="module">
    export const createToast = (msg, type="primary") => Toast.create({ message: msg, position:"is-top", type:`is-${type}`})
    export function browse({filetype="", dir=true}={}) {
        return new Promise((resolve, reject)=>{

            const mainWindow = remote.getCurrentWindow()
            let type;
            dir ? type = "openDirectory" : type = "openFile"

            const options = {
                filters: [
                    { name: filetype, extensions: [`*${filetype}`] },
                    { name: 'All Files', extensions: ['*'] }

                ],
                properties: [type, "multiSelections"],
            }
            remote.dialog.showOpenDialog(mainWindow, options)
            .then(result => {
                console.log(result.canceled)
                console.log(result.filePaths)
                resolve(result)
            }).catch(err => { 
                createToast("Couldn't open folder", "danger")
                reject(err) })
        })
    }

</script>

<script>
    
    // IMPORTING MODULES
    import IconButton, {Icon} from '@smui/icon-button';
    import { fly, slide } from 'svelte/transition';
    import Textfield from '@smui/textfield';
    import {onMount} from "svelte";
    import { Toast } from 'svelma'
    // import {activated, modalContent, modalTitle} from "./Modal.svelte"
    import FileBrowser from "./FileBrowser.svelte"
    
    ////////////////////////////////////////////////////////////////////////////

    // EXPORTED variables

    export let id;
    export let fileChecked=[];
    export let filetype = "felix"
    export let currentLocation = localStorage[`${filetype}_location`] || "";

    // let refresh = false;
    // onMount(()=>{if (currentLocation != "") {refresh = true}})

    function browse_folder() {
        browse({dir:true}).then(result=>{

            if (!result.canceled) {
                currentLocation= localStorage[`${filetype}_location`] = result.filePaths[0]
                // refresh = true;

            }
        })
        
    }

    let toggleBrowser = true;

</script>

<style lang="scss">

    $box1: #6a50ad59;
    .filebrowser, .fileContainer {
        background-image: url(./assets/css/intro.svg);
        height: calc(100vh - 7em);
    }

    .plotContainer {
        max-height: calc(100vh - 25em);
        overflow-y: auto;
        padding-bottom: 3em;
    }
     
    
    .filebrowser {
        padding-left: 2em;
        padding-top: 1em;
        background-color: $box1;
        border-radius: 0;
        
    }
    .fileContainer {margin: 0 2em; padding-bottom: 5rem; width: calc(70vw - 2em)}
    
    * :global(.box){background-color: #654ca25c;}
    * :global(.mdc-list-item){height: 2em;}
    * :global(.mdc-switch.mdc-switch--checked .mdc-switch__thumb, .mdc-switch.mdc-switch--checked .mdc-switch__track){background-color: #ffffff}
    * :global(.material-icons) {margin-right:0.2em; cursor:pointer;}
    * :global(.align) { display: flex; align-items: center; flex-wrap: wrap; }
    * :global(.center) {justify-content: center;}
    * :global(.gap) {margin-right: 2em;}
    .buttonContainer {
        max-height: 20em;
        overflow-y: auto;
    }
    .box {border-radius: 0;}
    .container {min-height: calc(100vh - 10em);}
    .plotContainer > div {margin-top: 1em;}
</style>

<section {id} style="display:none" class="animated fadeIn">
    <div class="columns">

        {#if toggleBrowser}
            <div class="column is-one-fifth-widescreen is-one-quarter-desktop box filebrowser" transition:fly="{{ x: -100, duration: 500 }}">
                <FileBrowser bind:currentLocation {filetype} bind:fileChecked />

            </div>
        {/if}

        <div class="column fileContainer">
            <div class="container button-plot-container box">

                <div class="align">
                    <IconButton  toggle bind:pressed={toggleBrowser}>
                        <Icon class="material-icons" on>menu_open</Icon>
                        <Icon class="material-icons" >menu</Icon>
                    </IconButton>
                    <button class="button is-link gap" on:click={browse_folder}>Browse</button>
                    <Textfield style="margin-bottom:1em;" bind:value={currentLocation} label="Current location" />
                </div>

                <div class="align buttonContainer"> <slot name="buttonContainer" /></div>
                <div class="plotContainer"> <slot name="plotContainer" /> </div>
                
            </div>
        </div>

    </div>
</section>