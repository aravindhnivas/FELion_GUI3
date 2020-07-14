
<script context="module">
    export const toggleFileDetailsTable = writable(false)
</script>

<script>
    import { filedetails } from "../../functions/svelteWritables";
    import CustomIconSwitch from '../../../../components/CustomIconSwitch.svelte';

    import Table from '../../../../components/Table.svelte';
    import { createEventDispatcher } from 'svelte';
    import { writable } from 'svelte/store';

    import { savefile,  loadfile } from '../../functions/misc';

    export let plotData;
    
    const dispatch = createEventDispatcher();

    function loadfiledetails(){
        const loadedfile = loadfile({name:"filedetails"})
        $filedetails = _.uniqBy([...loadedfile, ...$filedetails], "filename")
    }

</script>

<div class=""> 

    <div style="display:flex;">
        <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"get_details"})}">Get details</button>
        <CustomIconSwitch bind:toggler={$toggleFileDetailsTable} icons={["arrow_drop_down", "arrow_drop_up"]}/>
        <button class="button is-link" on:click="{()=>savefile({file:$filedetails, name:"filedetails"})}">Save</button>
        <button class="button is-link" on:click="{loadfiledetails}">Load</button>
    </div>
    
    {#if $toggleFileDetailsTable}
        <Table head={["Filename", "min(cm-1)", "max(cm-1)", "Trap(s)", "B0(ms)", "Res.(V)", "IE(eV)", "Temp(K)","Precursor", ]} bind:rows={$filedetails} keys={["filename", "min", "max", "trap", "b0", "res", "ie","temp", "precursor"]} tableid="felix_filedetails_table"/>
    {/if}
</div>