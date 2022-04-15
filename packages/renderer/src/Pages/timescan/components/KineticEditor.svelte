<script>
    import Editor                       from '$components/Editor.svelte'
    import {computeKineticCodeScipy}    from "../functions/computeKineticCode"

    export let ratek3;
    export let ratekCID;
    export let reportRead=false;
    export let reportSaved=false;
    export let massOfReactants;
    export let nameOfReactants;
    export let kineticEditorFilename;
    export let kineticEditorLocation;

    let editor
</script>

<div class="report-editor-div" id="kinetics-editor__div">
    <Editor filetype="kinetics" showReport={true}
        mount="#kinetics-editor__div" id="kinetics-editor"
        mainTitle="Kinetic Code" bind:editor
        savefilename={kineticEditorFilename}
        bind:location={kineticEditorLocation}
        bind:reportSaved bind:reportRead
        >
        <svelte:fragment slot="btn-row">
            <button class="button is-warning" 
                on:click={()=>{
                    if(!massOfReactants) return window.createToast("No data available", "danger")
                    const dataToSet = computeKineticCodeScipy({
                        ratek3, ratekCID, nameOfReactants
                    })
                    if(dataToSet) {
                        reportSaved = false; editor?.setData(dataToSet);
                        console.info("data comupted")
                    }
                }}>compute</button>
        </svelte:fragment>
    </Editor>

</div>