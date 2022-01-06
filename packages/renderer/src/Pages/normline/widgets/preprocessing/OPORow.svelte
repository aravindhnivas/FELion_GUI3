<script>
    import {
        opoMode,
        baselineFile,
        felixPlotAnnotations
    }                       from "../../functions/svelteWritables";
    import {opofile_func}   from '../../functions/opofile';
    import { fade }         from 'svelte/transition';
    
    import CustomSelect     from '$components/CustomSelect.svelte';
    import QuickBrowser     from '$components/QuickBrowser.svelte';
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'

    import computePy_func   from "$src/Pages/general/computePy"

    /////////////////////////////////////////////////////////////////////////


    export let OPOLocation
    export let opofiles
    export let OPOfilesChecked
    export let graphPlotted
    export let removeExtraFile;
    let showOPOFiles =false, OPOcalibFiles = [];
    let deltaOPO = 0.3, calibFile = "", opoPower=1;
    
    $: if(fs.existsSync(OPOLocation)) {
        OPOcalibFiles = fs.readdirSync(OPOLocation).filter(file=> file.endsWith(".calibOPO"))
        opofiles = OPOfilesChecked.map(file=>pathResolve(OPOLocation, file))
    }

    function plotData({e=null, tkplot="run"}={}){
        let pyfile="oposcan", args;
        removeExtraFile()
        if(opofiles.length<1) return window.createToast("No files selected", "danger")
        $opoMode = true, $felixPlotAnnotations = []
        
        let opo_args = {opofiles, tkplot, deltaOPO, calibFile, opoPower}

        args=[JSON.stringify(opo_args)]
        computePy_func({e, pyfile, args})
        .then((dataFromPython)=>{
            opofile_func({dataFromPython, delta:deltaOPO})
            window.createToast("Graph Plotted", "success")
            graphPlotted = true, $opoMode = true
            showOPOFiles=false
        })

    }

</script>

<QuickBrowser
    title="OPO files"
    filetype="ofelix"
    bind:active={showOPOFiles}
    bind:currentLocation={OPOLocation}
    bind:fileChecked={OPOfilesChecked}
    on:submit="{(e)=>{plotData({e:e.detail.event})}}"
    on:markedFile="{(e)=>$baselineFile = e.detail.markedFile}"
/>

{#if $opoMode}
    <div class="align" transition:fade >
        <span class="tag is-warning " >OPO Mode: </span>
        <CustomSelect bind:picked={calibFile} label="Calib. file" options={OPOcalibFiles}/>
        <CustomTextSwitch style="width:7em;" step="0.1" variant="outlined" bind:value={deltaOPO} label="Delta OPO"/>
        <CustomTextSwitch style="width:9em" step="0.1" variant="outlined" bind:value={opoPower} label="Power (mJ)"/>
        <button class="button is-link" on:click="{()=>{showOPOFiles = !showOPOFiles;}}"> Browse File</button>
        <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Replot</button>
    
    </div>
{/if}
