
<script>

    import { filedetails, opoMode } from "../../functions/svelteWritables";
    import CustomIconSwitch from '../../../../components/CustomIconSwitch.svelte';
    import Table from '../../../../components/Table.svelte';
    import { savefile,  loadfile } from '../../functions/misc';

    import {computePy_func} from '../../functions/computePy';
    
    import {get_details_func} from '../../functions/get_details';
    export let felixfiles, normMethod;

    let toggleFileDetailsTable = false
    
    function plotData({e=null}={}){
        
        let pyfile="getfile_details.py", args;
        
        if(felixfiles.length<1) return createToast("No files selected", "danger")
        
        args=[JSON.stringify({files:$opoMode?opofiles : felixfiles, normMethod})]
        computePy_func({e, pyfile, args})
        .then((dataFromPython)=>{ get_details_func({dataFromPython}); toggleFileDetailsTable = true })
        .catch(err=>{preModal.modalContent = err;  preModal.open = true})
        
    }

    function loadfiledetails(){
        const loadedfile = loadfile({name:"filedetails"})
        $filedetails = _.uniqBy([...loadedfile, ...$filedetails], "filename")
    }
</script>

<div class="align"> 
    <div style="display:flex;">

        <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Get details</button>
    
        <CustomIconSwitch bind:toggler={toggleFileDetailsTable} icons={["arrow_drop_down", "arrow_drop_up"]}/>
        <button class="button is-link" on:click="{()=>savefile({file:$filedetails, name:"filedetails"})}">Save</button>
        <button class="button is-link" on:click="{loadfiledetails}">Load</button>
    
    
    </div>
    
    {#if toggleFileDetailsTable}
        <Table head={["Filename", "min(cm-1)", "max(cm-1)", "Trap(s)", "B0(ms)", "Res.(V)", "IE(eV)", "Temp(K)","Precursor", ]} bind:rows={$filedetails} keys={["filename", "min", "max", "trap", "b0", "res", "ie","temp", "precursor"]} tableid="felix_filedetails_table"/>
    
    {/if}
</div>