
<script>
    import { felixOutputName, collectData } from "../../functions/svelteWritables";
    import Textfield from '@smui/textfield';
    import CustomSelect from '../../../../components/CustomSelect.svelte';
    import CustomSwitch from '../../../../components/CustomSwitch.svelte';
    import { createEventDispatcher } from 'svelte';

    export let output_namelists, writeFileName, writeFile, overwrite_expfit;
    const dispatch = createEventDispatcher();
    
</script>

<div class="content" >
    <CustomSelect bind:picked={$felixOutputName} label="Output filename" options={output_namelists}/>

    <Textfield style="width:7em; margin:0 0.5em;" bind:value={writeFileName} label="writeFileName"/>
    <CustomSwitch style="margin: 0 1em;" bind:selected={writeFile} label="Write"/>
    <CustomSwitch style="margin: 0 1em;" bind:selected={overwrite_expfit} label="Overwrite"/>
    <CustomSwitch style="margin: 0 1em;" bind:selected={$collectData} label="Collect"/>
    <button class="button is-link" on:click="{()=>dispatch("addfile")}">Add files</button>
    <button class="button is-link" on:click="{()=>dispatch("removefile")}">Remove files</button>
</div>