
<script>
    import {mainPreModal} from "../../../../svelteWritable";
    import {toggleRow, felixopoLocation} from "../../functions/svelteWritables";
    import Textfield from '@smui/textfield';
    import QuickBrowser from '../../../../components/QuickBrowser.svelte';
    import { fade } from 'svelte/transition';
    
    import {theory_func} from '../../functions/theory';

    import CustomSwitch from '../../../../components/CustomSwitch.svelte';
    export let theoryLocation, show_theoryplot, normMethod;

    let sigma=7, scale=1, theoryfiles=[], tkplot=false;
    let showTheoryFiles = false, theoryfilesChecked = []
    $: if(fs.existsSync(theoryLocation)) { theoryfiles =theoryfilesChecked.map(file=>path.resolve(theoryLocation, file)) }

    function plotData(e=null){
        let pyfile="theory.py", args;
        
        if(theoryfiles.length < 1) return window.createToast("No files selected", "danger")
        
        args={theoryfiles, normMethod, sigma, scale, currentLocation:$felixopoLocation, tkplot, onlyExpRange}
        args=[JSON.stringify(args)]
        computePy_func({e, pyfile, args})
        .then((dataFromPython)=>{
            theory_func({dataFromPython, normMethod})
            window.createToast("Graph Plotted", "success")
            show_theoryplot = true, showTheoryFiles = false
        }).catch(error=>{mainPreModal.error(error.stack || error)})
    }

    let onlyExpRange = false;
    $: if(theoryLocation) {db.set("theoryLocation", theoryLocation)}
</script>

<QuickBrowser title="Theory files" bind:active={showTheoryFiles} bind:currentLocation={theoryLocation} bind:fileChecked={theoryfilesChecked} on:submit="{(e)=>{plotData(e.detail.event);}}"/>

{#if $toggleRow}
    <div class="align" transition:fade>

        <button class="button is-link" on:click="{()=>{showTheoryFiles = !showTheoryFiles;}}"> Browse File</button>
        <Textfield style="width:7em; margin-right:0.5em;" variant="outlined" bind:value={sigma} label="Sigma" input$type="number" input$step="0.5" input$min="0"/>


        <Textfield style="width:7em" variant="outlined" bind:value={scale} label="Scale" input$type="number" input$step="0.01" input$min="0" input$max="1"/>
        
        <CustomSwitch style="margin: 0 1em;" bind:selected={onlyExpRange} label="Only Exp. Range"/>
        <CustomSwitch style="margin: 0 1em;" bind:selected={tkplot} label="Matplotlib"/>
        
        <button class="button is-link" on:click="{plotData}">Replot</button>
    </div>
{/if}