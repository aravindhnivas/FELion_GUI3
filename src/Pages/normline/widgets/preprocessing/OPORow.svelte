<script>
    import {opoMode} from "../../functions/svelteWritables";
    import Textfield from '@smui/textfield';
    import CustomSelect from '../../../../components/CustomSelect.svelte';
    import QuickBrowser from '../../../../components/QuickBrowser.svelte';
    import { fade } from 'svelte/transition';
    export let deltaOPO, calibValue, calibFile, OPOLocation, opofiles, OPOfilesChecked, plotData;

    let showOPOFiles =false, OPOcalibFiles = []
    
    
    $: if(fs.existsSync(OPOLocation)) {
    
        OPOcalibFiles = fs.readdirSync(OPOLocation).filter(file=> file.endsWith(".calibOPO"))
        opofiles = OPOfilesChecked.map(file=>path.resolve(OPOLocation, file))
    }

    function plotOPO(e) {

        plotData({e:e.detail.event, filetype:"opofile"});
        localStorage["opoLocation"] = OPOLocation; 
        showOPOFiles=false

    }

</script>

<QuickBrowser bind:active={showOPOFiles} bind:currentLocation={OPOLocation} bind:fileChecked={OPOfilesChecked} filetype="ofelix" on:submit="{(e)=>{plotOPO(e)}}"/>

{#if $opoMode}

    <div class="align" transition:fade>

        <CustomSelect style="width:7em;" bind:picked={calibFile} label="Calib. file" options={["", ...OPOcalibFiles]}/>
        <Textfield style="width:7em; margin:0 0.5em;" variant="outlined" bind:value={deltaOPO} label="Delta OPO"/>
        <Textfield style="width:9em"  variant="outlined" bind:value={calibValue} label="Wn-meter calib."/>
        <button class="button is-link" on:click="{()=>{showOPOFiles = !showOPOFiles;}}"> Browse File</button>

        <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"opofile"})}">Replot</button>
    </div>

{/if}