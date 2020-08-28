
<script>

    import {opoMode, felixPlotAnnotations} from "../../functions/svelteWritables";
    import Textfield from '@smui/textfield';
    import CustomSelect from '../../../../components/CustomSelect.svelte';
    import QuickBrowser from '../../../../components/QuickBrowser.svelte';

    import { fade } from 'svelte/transition';
    import {opofile_func} from '../../functions/opofile';

    export let OPOLocation, opofiles, OPOfilesChecked, preModal, graphPlotted, removeExtraFile;

    let showOPOFiles =false, OPOcalibFiles = [];

    let deltaOPO = 0.3, calibFile = "", opoPower=1;
    
    
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
            localStorage["opoLocation"] = OPOLocation; 
            showOPOFiles=false
        }).catch(err=>{preModal.modalContent = err;  preModal.open = true})

    }

</script>

<QuickBrowser title="OPO files" bind:active={showOPOFiles} bind:currentLocation={OPOLocation} bind:fileChecked={OPOfilesChecked} filetype="ofelix" on:submit="{(e)=>{plotData({e:e.detail.event})}}"/>

{#if $opoMode}

    <div class="align" transition:fade>

        <CustomSelect style="width:7em;" bind:picked={calibFile} label="Calib. file" options={["", ...OPOcalibFiles]}/>
        
        <Textfield style="width:7em; margin:0 0.5em;" type="number" step="0.02" min="0" variant="outlined" bind:value={deltaOPO} label="Delta OPO"/>
        <Textfield style="width:9em" type="number" step="0.1" min="0" variant="outlined" bind:value={opoPower} label="Power (mJ)"/>

        <button class="button is-link" on:click="{()=>{showOPOFiles = !showOPOFiles;}}"> Browse File</button>
        <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Replot</button>
        <!-- <button class="button is-warning" >OPO MODE</button> -->

    </div>
    
{/if}