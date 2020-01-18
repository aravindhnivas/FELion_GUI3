<script>
    // IMPORTING Modules
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text/index';
    import Layout from "../components/Layout.svelte"
    import { fly } from 'svelte/transition';
    ///////////////////////////////////////////////////////////////////////

    // Variables
    let filetype="felix", id="Normline", felixfiles=[], delta=1, toggleRow=false;
    let location = localStorage[`${filetype}_location`] || ""
    $: console.log("Normline update: ", location)

    // Modal variable
    let modalContent="", modalTitle="", activated = false;
</script>


<style>
    * :global(.button) {margin: 0.4em;}
    * :global(.short-input) {
        width: 7em;
        margin: 0 1em;
    }
    * :global(.mdc-text-field--outlined) {height: 2.5em;}

</style>

<Layout {filetype} {id} bind:currentLocation={location} bind:fileChecked={felixfiles} bind:activated {modalContent} {modalTitle}>

    <div class="buttonSlot" slot="buttonContainer">
        <div class="align">

            <button class="button is-link">Create Baseline</button>
            <button class="button is-link">FELIX Plot</button>
            <button class="button is-link" on:click="{()=>toggleRow = !toggleRow}">Add Theory</button>
            <button class="button is-link">Open in Matplotlib</button>
            <button class="button is-link">OPO</button>

            <div class="short-input"><Textfield variant="outlined" bind:value={delta} label="Delta value" /></div>

        </div>

        {#if toggleRow}
            <div class="align" transition:fly="{{ y: -20, duration: 500 }}">
                <button class="button is-link">Create Baseline</button>
                <button class="button is-link">Create Baseline</button>
                <button class="button is-link">Create Baseline</button>
                <button class="button is-link">Create Baseline</button>
                <button class="button is-link">Create Baseline</button>
            </div>
        {/if}
    </div>

</Layout> 