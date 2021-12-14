
<script>

    import {opoMode, felixPlotAnnotations, baselineFile} from "../../functions/svelteWritables";
    import CustomSelect from '$components/CustomSelect.svelte';
    import QuickBrowser from '$components/QuickBrowser.svelte';
    import { fade } from 'svelte/transition';
    import {opofile_func} from '../../functions/opofile';
    export let OPOLocation, opofiles, OPOfilesChecked, graphPlotted, removeExtraFile;
    import CustomTextSwitch         from '$components/CustomTextSwitch.svelte'
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
        }).catch(error=>{window.handleError(error)})

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
        <CustomSelect style="width:7em;" bind:picked={calibFile} label="Calib. file" options={OPOcalibFiles}/>
        <CustomTextSwitch style="width:7em;" step="0.1" variant="outlined" bind:value={deltaOPO} label="Delta OPO"/>
        <CustomTextSwitch style="width:9em" step="0.1" variant="outlined" bind:value={opoPower} label="Power (mJ)"/>
        <button class="button is-link" on:click="{()=>{showOPOFiles = !showOPOFiles;}}"> Browse File</button>
        <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Replot</button>
    
    </div>
{/if}
