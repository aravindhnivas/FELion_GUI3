<script>
    import ClassicEditor from '$static/assets/js/ckeditor5';
    import {browse} from '$components/Layout.svelte';
    export let id = window.getID();
    export let location = ""
    export let filetype = ""
    export let editor;

    
    async function mountEditor(node) {
        try {
            editor = await ClassicEditor.create( node, {toolbar: {shouldNotGroupWhenFull: true}})
            return {destroy() {editor.destroy().catch(window.handleError)} }
    
        } catch (error) {window.handleError( error );}
    }

    $: reportFile = window.pathJoin(location, "report.md")

    
    
    async function browse_folder() {
        try {
            [location] = await browse({dir:true})
            console.log(location)
            // if(location) {
            //     reportFile = window.pathJoin(location, "report.md")
            // }
        } catch (error) {window.handleError( error )}
    }

    const saveReport = () => {
        try {
            if(location) {
                fs.writeFileSync( reportFile, editor.getData() )
                window.createToast("report.md file saved", "link")
            }
        } catch (error) {window.handleError( error )}
    }
    let reportWindowClosed = true;
    // let graphWindow;
    function openReport() {
        
        const mount = document.querySelector(`#${filetype}-plotContainer-report-editor-div`)
        const graphWindow = new WinBox({
            root: document.getElementById("pageContainer"), mount,
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
        
    }

</script>

<style global >
    .ck.ck-content * {color: black;}
    .ck-editor { min-height: 10em;}
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
    .wb-body > .report-editor-div {
        padding: 1em;
        display: grid;
        gap: 1em;
    }

</style>

<div class="align v-center">

    <div class="notice__div">
        Report/Editor
        {#if reportWindowClosed}
            <i class="material-icons" on:click="{openReport}">zoom_out_map</i>
        {/if}
    </div>
    <button class="button is-link" on:click="{browse_folder}">Browse</button>
    <button class="button is-link" on:click="{saveReport}">Save</button>
</div>

<div class="ckeditor-svelte content" {id} use:mountEditor >
    
    {#if window.fs.existsSync(reportFile)}
        
    {@html window.marked(window.fs.readFileSync(reportFile))}

    {:else}
        <h1>{filetype.toUpperCase()} Report</h1>
    
    {/if}


</div>