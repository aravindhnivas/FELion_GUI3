
<script>
    import {toggleRow} from "../../functions/svelteWritables";
    import Textfield from '@smui/textfield';
    import QuickBrowser from '../../../../components/QuickBrowser.svelte';
    import { fade } from 'svelte/transition';
    // import {computePy_func} from '../../functions/computePy';
    
    import {theory_func} from '../../functions/theory';
    import {createToast} from '../../functions/misc';

    export let theoryLocation, currentLocation, show_theoryplot, normMethod, preModal;

    let sigma=20, scale=1, theoryfiles=[]
    
    let showTheoryFiles = false, theoryfilesChecked = []

    $: if(fs.existsSync(theoryLocation)) { theoryfiles =theoryfilesChecked.map(file=>path.resolve(theoryLocation, file)) }

    function plotData({e=null, tkplot="run"}={}){
        let pyfile="theory.py", args;
        
        if(theoryfiles.length < 1) return createToast("No files selected", "danger")
        
        args=[...theoryfiles, normMethod, sigma, scale, currentLocation, tkplot]
        computePy_func({e, pyfile, args})
        .then((dataFromPython)=>{
            theory_func({dataFromPython, normMethod})
            createToast("Graph Plotted", "success")
            show_theoryplot = true, showTheoryFiles = false
        }).catch(err=>{preModal.modalContent = err;  preModal.open = true})
    }

</script>

<QuickBrowser title="Theory files" bind:active={showTheoryFiles} bind:currentLocation={theoryLocation} bind:fileChecked={theoryfilesChecked} on:submit="{(e)=>{plotData({e:e.detail.event}); localStorage["theoryLocation"] = theoryLocation}}"/>

{#if $toggleRow}

    <div class="align" transition:fade>

        <button class="button is-link" on:click="{()=>{showTheoryFiles = !showTheoryFiles;}}"> Browse File</button>
        <Textfield type="number" style="width:7em; margin-right:0.5em;" variant="outlined" bind:value={sigma} label="Sigma"/>
        <Textfield type="number" style="width:7em" variant="outlined" bind:value={scale} label="Scale"/>
        <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Replot</button>
    </div>
{/if}