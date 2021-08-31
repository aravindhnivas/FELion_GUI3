
<script>

    import {opoMode, felixPlotAnnotations, felixConfigDB, baselineFile} from "../../functions/svelteWritables";
    import {mainPreModal} from "../../../../svelteWritable";
    import Textfield from '@smui/textfield';
    import CustomSelect from '../../../../components/CustomSelect.svelte';
    import QuickBrowser from '../../../../components/QuickBrowser.svelte';
    import { fade } from 'svelte/transition';
    import {opofile_func} from '../../functions/opofile';
    export let OPOLocation, opofiles, OPOfilesChecked, graphPlotted, removeExtraFile;
    export let updateConfig=false;

    let showOPOFiles =false, OPOcalibFiles = [];

    let deltaOPO = 0.3, calibFile = "", opoPower=1;
    
    let odelta=$felixConfigDB.get("odelta");

    
    function loadConfig() {
        odelta =  $felixConfigDB.get("odelta")
        console.log("odelta updated", odelta)
    }
    $: if(updateConfig) loadConfig()

    $: if(fs.existsSync(OPOLocation)) {
    
        OPOcalibFiles = fs.readdirSync(OPOLocation).filter(file=> file.endsWith(".calibOPO"))
        opofiles = OPOfilesChecked.map(file=>path.resolve(OPOLocation, file))
    }

    function plotData({e=null, tkplot="run"}={}){
        let pyfile="oposcan.py", args;
        
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
        }).catch(error=>{mainPreModal.error(error.stack || error)})

    }
    // $: console.log(OPOfilesChecked)
</script>

<QuickBrowser title="OPO files" bind:active={showOPOFiles} bind:currentLocation={OPOLocation} bind:fileChecked={OPOfilesChecked} filetype="ofelix" on:submit="{(e)=>{plotData({e:e.detail.event})}}" on:markedFile="{(e)=>$baselineFile = e.detail.markedFile}"/>

{#if $opoMode}

    <div class="align" transition:fade>

        <CustomSelect style="width:7em;" bind:picked={calibFile} label="Calib. file" options={["", ...OPOcalibFiles]}/>
        
        <Textfield style="width:7em; margin:0 0.5em;" input$type="number" input$step={odelta} input$min="0" variant="outlined" bind:value={deltaOPO} label="Delta OPO"/>
        <Textfield style="width:9em" input$type="number" input$step="0.1" input$min="0" variant="outlined" bind:value={opoPower} label="Power (mJ)"/>

        <button class="button is-link" on:click="{()=>{showOPOFiles = !showOPOFiles;}}"> Browse File</button>
        <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Replot</button>
        <!-- <button class="button is-warning" >OPO MODE</button> -->

    </div>
    
{/if}