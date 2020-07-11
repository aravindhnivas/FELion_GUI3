
<script>
    import Modal1 from '../../../components/Modal1.svelte';
    import Textfield from '@smui/textfield';
    import { createEventDispatcher } from 'svelte';
    import {browse} from "../../../components/Layout.svelte"
    export let addFileModal=false, addedFileCol=1, addedFileScale=1000, addedfiles=[], addedFile={};

    const dispatch = createEventDispatcher();

    function addFileSelection() {
        browse({dir:false}).then(result=>{ 

            if (!result.canceled) {addedfiles = addedFile["files"] = result.filePaths}  
        })
    }

</script>


{#if addFileModal}

    <Modal1 bind:active={addFileModal} title="Add file to plot">

        <div slot="content" >
            <Textfield style="width:7em; margin:0 0.5em;" bind:value={addedFileCol} label="Columns"/>
            <Textfield style="width:7em; margin:0 0.5em;" bind:value={addedFileScale} label="ScaleY"/>
            <button on:click={addFileSelection} class="button is-link">Browse</button>

        </div>
        <button slot="footerbtn" class="button is-link" on:click="{(e)=>dispatch('addfile', { event:e })}" >Add</button>
    </Modal1>
    
{/if}