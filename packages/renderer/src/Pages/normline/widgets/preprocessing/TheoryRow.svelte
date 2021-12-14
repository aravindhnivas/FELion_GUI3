
<script>
    import {toggleRow, felixopoLocation} from "../../functions/svelteWritables";
    import CustomTextSwitch         from '$components/CustomTextSwitch.svelte'
    import QuickBrowser from '$components/QuickBrowser.svelte';
    import { fade } from 'svelte/transition';
    import {theory_func} from '../../functions/theory';
    import CustomSwitch from '$components/CustomSwitch.svelte';
    export let theoryLocation, show_theoryplot, normMethod;

    let sigma=7, scale=1, theoryfiles=[], tkplot=false;
    let showTheoryFiles = false, theoryfilesChecked = []
    $: if(fs.existsSync(theoryLocation)) { theoryfiles =theoryfilesChecked.map(file=>pathResolve(theoryLocation, file)) }

    function plotData(e=null){
        let pyfile="theory", args;
        
        if(theoryfiles.length < 1) return window.createToast("No files selected", "danger")
        
        args={theoryfiles, normMethod, sigma, scale, currentLocation:$felixopoLocation, tkplot, onlyExpRange}
        args=[JSON.stringify(args)]
        computePy_func({e, pyfile, args})
        .then((dataFromPython)=>{
            theory_func({dataFromPython, normMethod})
            window.createToast("Graph Plotted", "success")
            show_theoryplot = true, showTheoryFiles = false
        }).catch(error=>{window.handleError(error)})
    }

    let onlyExpRange = false;
    $: if(theoryLocation) {db.set("theoryLocation", theoryLocation)}

</script>

<QuickBrowser title="Theory files"
    bind:active={showTheoryFiles}
    bind:currentLocation={theoryLocation}
    bind:fileChecked={theoryfilesChecked}
    on:submit="{(e)=>{plotData(e.detail.event);}}"
/>

{#if $toggleRow}

    <div class="align" transition:fade>
        <button class="button is-link" on:click="{()=>{showTheoryFiles = !showTheoryFiles;}}"> Browse File</button>
        <CustomTextSwitch style="width:7em;" variant="outlined" bind:value={sigma} label="Sigma" step="0.5" />
        <CustomTextSwitch style="width:7em" variant="outlined" bind:value={scale} label="Scale" step="0.001" max="1" />
        <CustomSwitch style="margin: 0 1em;" bind:selected={onlyExpRange} label="Only Exp. Range"/>
        <CustomSwitch style="margin: 0 1em;" bind:selected={tkplot} label="Matplotlib"/>
        <button class="button is-link" on:click="{plotData}">Replot</button>
    
    </div>

{/if}