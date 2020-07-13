
<script>
    import Modal from '../../../components/Modal.svelte';
    import Textfield from '@smui/textfield';
    import { createEventDispatcher } from 'svelte';
    import {browse} from "../../../components/Layout.svelte"
    export let active=false, addedFileCol=1, addedFileScale=1000, addedfiles=[], addedFile={};

    const dispatch = createEventDispatcher();

    function addFileSelection() {
        browse({dir:false}).then(result=>{ 

            if (!result.canceled) {addedfiles = addedFile["files"] = result.filePaths}  
        })
    }

</script>


{#if active}

    <Modal bind:active title="Add file to plot">

        <div slot="content" >
            <Textfield style="width:7em; margin:0 0.5em;" bind:value={addedFileCol} label="Columns"/>
            <Textfield style="width:7em; margin:0 0.5em;" bind:value={addedFileScale} label="ScaleY"/>
            <button on:click={addFileSelection} class="button is-link">Browse</button>

        </div>
        <button slot="footerbtn" class="button is-link" on:click="{(e)=>dispatch('addfile', { event:e })}" >Add</button>
    </Modal>
    
{/if}