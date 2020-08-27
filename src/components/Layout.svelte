<script context="module">
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

            if (process.versions.electron >= "7") {
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
    
    import { fly } from 'svelte/transition';
    import Textfield from '@smui/textfield';
    import {onMount} from "svelte";
    import FileBrowser from "./FileBrowser.svelte"
    import Hamburger1 from "../components/icon_animations/Hamburger1.svelte";

    import { createEventDispatcher } from 'svelte';
    import PreModal from "./PreModal.svelte";

    ////////////////////////////////////////////////////////////////////////////

    export let id, fileChecked=[], filetype = "felix", toggleBrowser = false, preModal = {};
    export let currentLocation = localStorage[`${filetype}_location`] || "";
    const dispatch = createEventDispatcher()

    function browse_folder() {
        browse({dir:true}).then(result=>{
            if (!result.canceled) { currentLocation= localStorage[`${filetype}_location`] = result.filePaths[0] }
        })

    }

    function tour_event() { dispatch('tour', {filetype}) }

    onMount(()=>{ toggleBrowser = true; })

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
        overflow-y: auto; padding-bottom: 12em; max-height: calc(100vh - 27em);

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

</style>

<PreModal bind:preModal />


<section {id} style="display:none" class="animated fadeIn">

    <div class="columns">

        {#if toggleBrowser}
            <div class="column is-one-fifth-widescreen is-one-quarter-desktop box filebrowser adjust-right" transition:fly="{{ x: -100, duration: 500 }}">
                <FileBrowser bind:currentLocation {filetype} bind:fileChecked on:chdir/>
            </div>
        {/if}

        <div class="column fileContainer" >

            <div class="container button-plot-container box">
                <div class="align">


                    <Hamburger1 bind:active={toggleBrowser}/>
                    <button class="button is-link gap" id="{filetype}_filebrowser_btn" on:click={browse_folder}>Browse</button>

                    <Textfield style="margin-bottom:1em; width:70%;" bind:value={currentLocation} label="Current location" />
                    <button class="button is-link is-pulled-right" on:click={tour_event}>Need help?</button>

                </div>
                <div class="align buttonContainer"> <slot name="buttonContainer" /></div>
                <div class="plotContainer"> <slot name="plotContainer" /> </div>
            </div>
        </div>
    </div>
    
</section>