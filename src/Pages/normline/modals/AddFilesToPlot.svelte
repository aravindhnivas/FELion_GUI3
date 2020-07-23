
<script>
    import {graphDiv} from '../functions/svelteWritables';
    import Modal from '../../../components/Modal.svelte';
    import Textfield from '@smui/textfield';
    import {browse} from "../../../components/Layout.svelte";
    import {computePy_func} from '../functions/computePy';

    import {createToast} from '../functions/misc';
    
    export let active=false, fileChecked=[], addedFileCol=1, addedFileScale=1000, addedfiles=[], addedFile={}, extrafileAdded=0, preModal;


    function addFileSelection() {

        browse({dir:false}).then(result=>{  if (!result.canceled) {addedfiles = addedFile["files"] = result.filePaths} })
        
    }

    function plotData({e=null}={}){

        let pyfile="addTrace.py" , args;
        
        if(addedFile.files < 1) return createToast("No files selected", "danger")
        addedFile["col"] = addedFileCol, addedFile["N"] = fileChecked.length + extrafileAdded

        addedFile["scale"] = addedFileScale
        args=[JSON.stringify(addedFile)]

        computePy_func({e, pyfile, args})
        .then((dataFromPython)=>{
            addFileModal = false
            Plotly.addTraces($graphDiv, dataFromPython)
            extrafileAdded += addedfiles.length
            createToast("Graph Plotted", "success")
        }).catch(err=>{preModal.modalContent = err;  preModal.open = true})

    }

</script>


{#if active}

    <Modal bind:active title="Add file to plot">

        <div slot="content" >
            <Textfield style="width:7em; margin:0 0.5em;" bind:value={addedFileCol} label="Columns"/>
            <Textfield style="width:7em; margin:0 0.5em;" bind:value={addedFileScale} label="ScaleY"/>
            <button on:click={addFileSelection} class="button is-link">Browse</button>

        </div>
        <button slot="footerbtn" class="button is-link" on:click="{(e)=>plotData({e:e})}" >Add</button>
    </Modal>
    
{/if}