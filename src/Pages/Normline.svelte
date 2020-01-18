<script>
    // IMPORTING Modules
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text/index';
    import Layout, {browse, createToast} from "../components/Layout.svelte"
    import { fly } from 'svelte/transition';
    import Ripple from '@smui/ripple';

    import {activated, modalContent} from "../components/Modal.svelte"
    import {bindDialog, filelist, filelistBinded} from "../components/DialogChecklist.svelte"
    console.log($bindDialog)
    ///////////////////////////////////////////////////////////////////////

    // Variables
    let filetype="felix", id="Normline", felixfiles=[], delta=1, toggleRow=false;

    let location = localStorage[`${filetype}_location`] || ""
    $: console.log(`${filetype} Update: \n${location}`)
    ///////////////////////////////////////////////////////////////////////

    // Theory file
    let sigma = 20, scale=1, thoeryfiles = [], theoryfile_location="";
    let theorylistDialog 
    let theoryfile_filtered;
    $: console.log("Filtered theory files: ", theoryfile_filtered)

    const get_theoryfiles = () => {
        browse({dir:false}).then(result=>{
            if (!result.canceled) {
                let files = result.filePaths
                theoryfile_location = path.dirname(files[0])
                $filelist = thoeryfiles = files.map(file=>file = path.basename(file))
                $filelistBinded = []
                createToast("Theoryfiles selected", "success")
            }
        }).catch(err=>{$modalContent = err; $activated=true})
    }

    ///////////////////////////////////////////////////////////////////////

</script>

<style>

    * :global(.button) {margin: 0.4em;}
    * :global(.short-input) {
        max-width: 7em;
        margin: 0 1em;
    }
    * :global(.mdc-text-field--outlined) {height: 2.5em;}

</style>

<Layout {filetype} {id} bind:currentLocation={location} bind:fileChecked={felixfiles}>

    <div class="buttonSlot" slot="buttonContainer">
        <div class="align">

            <button class="button is-link">Create Baseline</button>
            <button class="button is-link">FELIX Plot</button>
            <button class="button is-link" use:Ripple={[true, {color: 'primary'}]} tabindex="0" on:click="{()=>toggleRow = !toggleRow}">Add Theory</button>
            <button class="button is-link">Open in Matplotlib</button>
            <button class="button is-link">OPO</button>
            <div class="short-input"><Textfield variant="outlined" bind:value={delta} label="Delta value" /></div>

        </div>

        {#if toggleRow}
            <div class="align" transition:fly="{{ y: -20, duration: 500 }}">
                <button class="button is-link" on:click={get_theoryfiles}>Browse File</button>
                <button class="button is-link" on:click={$bindDialog.open}>Show files</button>
                <div class="short-input"><Textfield variant="outlined" bind:value={sigma} label="Sigma" /></div>
                <div class="short-input"><Textfield variant="outlined" bind:value={scale} label="Scale" /></div>
                <button class="button is-link">Open in Matplotlib</button>
                <button class="button is-link">Submit</button>
            </div>
        {/if}

    </div>

</Layout>