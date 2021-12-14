
<script>
    import { filedetails, opoMode } from "../../functions/svelteWritables";
    import CustomIconSwitch from '$components/CustomIconSwitch.svelte';
    import Table from '$components/Table.svelte';
    import { savefile,  loadfile } from '../../functions/misc';
    import {uniqBy} from "lodash-es"
    
    import {get_details_func} from '../../functions/get_details';
    export let felixfiles, normMethod;

    let toggleFileDetailsTable = false
    
    function plotData({e=null}={}){
        
        let pyfile="getfile_details", args;
        
        if(felixfiles.length<1) return window.createToast("No files selected", "danger")
        
        args=[JSON.stringify({files:$opoMode?opofiles : felixfiles, normMethod})]
        computePy_func({e, pyfile, args})
        .then((dataFromPython)=>{ get_details_func({dataFromPython}); toggleFileDetailsTable = true })
        .catch(error=>{window.handleError(error)})
        
    }

    function loadfiledetails(){
        const loadedfile = loadfile({name:"filedetails"})
        $filedetails = uniqBy([...loadedfile, ...$filedetails], "filename")
    }
</script>

<div class="align"> 
    <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Get details</button>
    <CustomIconSwitch bind:toggler={toggleFileDetailsTable} icons={["arrow_drop_down", "arrow_drop_up"]}/>
    <button class="button is-link" on:click="{()=>savefile({file:$filedetails, name:"filedetails"})}">Save</button>

    <button class="button is-link" on:click="{loadfiledetails}">Load</button>
    
    {#if toggleFileDetailsTable}
        <Table head={["Filename", "min(cm-1)", "max(cm-1)", "Trap(s)", "B0(ms)", "Res.(V)", "IE(eV)", "Temp(K)","Precursor", ]} bind:rows={$filedetails} keys={["filename", "min", "max", "trap", "b0", "res", "ie","temp", "precursor"]} id="felix_filedetails_table" closeOption={false} sortOption={true}/>

    {/if}

</div>