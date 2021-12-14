<script>
    import { onMount, onDestroy}    from "svelte"
    import Textfield                from '@smui/textfield';
    import { Remarkable }           from 'remarkable';
    import {browse}                 from '$components/Layout.svelte';
    import WinBox                   from "winbox/src/js/winbox.js";

    export let id = getID();
    export let location = ""
    export let filetype = ""
    export let editor="";
    export let mount=null;
    export let mainTitle="Report/Editor";
    
    export let savefilename="report";
    export let reportSaved = false;
    const md = new Remarkable();
    async function mountEditor(node) {
        try {
            editor = await ClassicEditor.create( node, {toolbar: {shouldNotGroupWhenFull: true}})
        } catch (error) {window.handleError( error );}
    }

    onDestroy(() => editor?.destroy())
    if(db.get(`${filetype}-report-md`)) {
        location = db.get(`${filetype}-report-md`)
    }

    $: reportFile = window.pathJoin(location , savefilename.endsWith(".md") ? savefilename : `${savefilename}.md`)
    let reportFiles = []

    const updateFiles = (node=null) => {
        node?.target?.classList.add("rotateIn")
        reportFiles = fs.readdirSync(pathResolve(location))
            .filter(name=>name.endsWith(".md"))
            .map(name=>name.replace(extname(name), ""))
    }

    $: if(fs.existsSync(location)) {
    
        db.set(`${filetype}-report-md`, location)
        updateFiles()
    }

    
    async function browse_folder() {

        const result = await browse()
        if(!result) return   

        location = result
        window.createToast("Location updated") 
    }

    const saveReport = () => {
        try {
            if(location) {
                fs.writeFileSync( reportFile, editor.getData() )
                reportSaved = true
                window.createToast(`${basename(reportFile)} file saved`, "link")
            }
        } catch (error) {window.handleError( error )}
    
    }

    let reportWindowClosed = true;
    function openReport() {
        
        const graphWindow = new WinBox({
            root: document.getElementById("pageContainer"), 
            mount: document.querySelector(mount),
            title: `Report ${filetype} `,
            x: "center", y: "center",
            width: "70%", height: "70%",
            background:"#634e96",
            top: 50, bottom:50,
            onclose: function(){
                reportWindowClosed = true
            },
        });
        
        reportWindowClosed = false;
        setTimeout(() => {
            graphWindow.focus()
        }, 100);
    }
    
    const readFromFile = () => {
        if(fs.existsSync(reportFile)) { editor?.setData(fs.readFileSync(reportFile)) }
    }

    onMount(()=>{
        return {destroy() {editor.destroy()}}
    })

</script>


<div class="report_main__div align">

    <div class="notice__div">
        {mainTitle}
        {#if reportWindowClosed}
            <i class="material-icons" on:click="{openReport}">zoom_out_map</i>
        {/if}
    </div>

    <div class="report_controler__div box">
        <div class="report_location__div" >
            <button class="button is-link" on:click="{browse_folder}">Browse</button>
            <Textfield bind:value={location} label="report location" />
            <Textfield bind:value={savefilename} label="report name" style="min-width: 70%;"/>

            <i class="material-icons animated faster" 
                on:animationend={({target})=>target.classList.remove("rotateIn")} 
                on:click="{updateFiles}">
                refresh
            </i>

        </div>
        <div class="btn-row">
            <slot name="btn-row"></slot>
            <button class="button is-warning" on:click={readFromFile}>read</button>
            <button class="button is-link" on:click="{saveReport}">Save</button>
        </div>
    </div>
</div>

<div class="ckeditor-svelte content" {id} use:mountEditor >
    
    {#if window.fs.existsSync(reportFile)}
        {@html md.render(window.fs.readFileSync(reportFile))}
    {:else}
        <h1>{filetype.toUpperCase()} Report</h1>

    {/if}
</div>


<style global lang="scss">

    .report-editor-div {
        display: grid;
        gap: 1em;
    }

    .ck.ck-content * {color: black;}
    .ck-editor { 
        min-height: 10em;
        width: 100%;
    }

    .ck-editor__main {
        overflow: auto;

        max-height: 25em;
    }
    .ck-content .table table {
        border: 2px double black;
        background: white;
    }
    .notice__div {
        width: 100%;
        background: #634e96;
        border: 1px solid;
        border-radius: 0.2em;
        padding: 0.2em;
        font-size: 25px;
        font-weight: bold;
        display: grid;
        grid-auto-flow: column;
        grid-template-columns: 1fr auto;
        align-items: center;
    }
    .editor-div * {color: black;}
    .wb-body {
        .report-editor-div {
            padding: 1em;
            display: grid;
            gap: 1em;
            height: 100%;
            grid-template-rows: auto 1fr;
            
            .ck-editor__main {
                max-height: calc(100% - 5em);
            }
            
        }
    }

    .report_location__div {
        display: grid;

        grid-template-columns: auto 3fr 1fr auto;
        width: 100%;
        gap: 1em;
        
        align-items: center;
    }

    .btn-row {
        
        display: flex;
        gap: 1em;
    }

    .report_main__div {
        .report_controler__div {
            display: grid;
            gap: 1em;

            width: 100%;
            margin: 0;
        }
    }

</style>