
<script>
    import {mainPreModal} from "../../../svelteWritable";
    import SeparateWindow from "../../../components/SeparateWindow.svelte";
    import CustomSelect from "../../../components/CustomSelect.svelte";
    import Textfield from '@smui/textfield';
    import {browse} from "../../../components/Layout.svelte";
    // import { plot } from "../../../js/functions";
    export let active;
    const title="Collisional rate constants"
    const plotID = "collisionalFitPlot"
    let graphWindow=null, windowReady=false;


    async function browse_file() {
        const result = await browse({dir:false})
        if (!result.canceled) { collisionlFile = result.filePaths[0] }
    }


    let collisionlFile = ""
    let saveFilename = ""
    let requiredTemp = 5
    let collisionalRateType = "";
    async function computeCollisionalFit(e) {
        try {
            const pyfile = "ROSAA/collisionalFit.py"
            const args = [JSON.stringify({collisionlFile, requiredTemp, saveFilename, collisionalRateType})]

            const dataFromPython = await computePy_func({e, pyfile, args})
        } catch (error) { $mainPreModal = {modalContent:error, open:true} }
    }

    $: if (windowReady) {setTimeout(()=>graphWindow.focus(), 100)}
</script>

<style lang="scss">
    
    .header {
        display: flex;
        gap: 1em;
        margin-bottom: 1em;
    }

    .graph__container {

        display: flex;
        flex-direction: column;
        row-gap: 1em;
        padding: 1em;
    
    }
</style>


{#if active}

    <SeparateWindow {title} bind:active bind:windowReady bind:graphWindow maximize={false}>

        <svelte:fragment slot="header_content__slot" >
            <div class="align">
                <CustomSelect options={["deexcitation", "excitation", "both"]} bind:picked={collisionalRateType} />
                <Textfield bind:value={saveFilename} label="saveFilename"/>
                <Textfield bind:value={requiredTemp} label="requiredTemp"/>
                <button class="button is-link" on:click={browse_file}>Browse</button>
                <button class="button is-link" on:click={computeCollisionalFit}>Compute</button>
            </div>
        </svelte:fragment>

        <svelte:fragment slot="main_content__slot">
            <div class="graph__container">
                <div id="{plotID}"></div>
            </div>
        </svelte:fragment>
    </SeparateWindow>
{/if}