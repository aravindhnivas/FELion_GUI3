
<script>
    import {toggleRow} from "../../functions/svelteWritables";
    import Textfield from '@smui/textfield';
    import QuickBrowser from '../../../../components/QuickBrowser.svelte';
    import { fade } from 'svelte/transition';
    export let theoryLocation, sigma, scale, theoryfiles, plotData;
    
    let showTheoryFiles = false, theoryfilesChecked = []

    $: if(fs.existsSync(theoryLocation)) { theoryfiles =theoryfilesChecked.map(file=>path.resolve(theoryLocation, file)) }
</script>

<QuickBrowser title="Theory files" bind:active={showTheoryFiles} bind:currentLocation={theoryLocation} bind:fileChecked={theoryfilesChecked} on:submit="{(e)=>{plotData({e:e.detail.event, filetype:"theory"}); localStorage["theoryLocation"] = theoryLocation}}"/>

{#if $toggleRow}

    <div class="align" transition:fade>

        <button class="button is-link" on:click="{()=>{showTheoryFiles = !showTheoryFiles;}}"> Browse File</button>
        <Textfield type="number" style="width:7em; margin-right:0.5em;" variant="outlined" bind:value={sigma} label="Sigma"/>
        <Textfield type="number" style="width:7em" variant="outlined" bind:value={scale} label="Scale"/>
        <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"theory"})}">Replot</button>
    </div>
{/if}