
<script>

    import {addTraces}  from 'plotly.js/dist/plotly';
    import Textfield    from '@smui/textfield';
    import Modal        from '$components/Modal.svelte';
    import {browse}     from "$components/Layout.svelte";
    import {graphDiv}   from '../functions/svelteWritables';
    
    export let active=false
    export let fileChecked=[]
    export let addedFileCol=1

    export let addedFileScale=1000
    export let addedfiles=[]
    export let addedFile={}
    export let extrafileAdded=0;

    async function addFileSelection() {

        const result = await browse({dir:false, multiple:true})
        if(!result) return
        addedfiles = addedFile["files"] = result
        window.createToast("Files added")
    }

    function plotData({e=null}={}){

        const pyfile="addTrace"
        let args;
        if(addedFile.files < 1) return window.createToast("No files selected", "danger")
        addedFile["col"] = addedFileCol, addedFile["N"] = fileChecked.length + extrafileAdded

        addedFile["scale"] = addedFileScale
        args=[JSON.stringify(addedFile)]

        computePy_func({e, pyfile, args})
        .then((dataFromPython)=>{
            addTraces($graphDiv, dataFromPython)
            extrafileAdded += addedfiles.length
            window.createToast("Graph Plotted", "success")
            active = false
        }).catch(error=>{window.handleError(error)})

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