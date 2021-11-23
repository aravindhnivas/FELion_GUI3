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

    let reportFile = window.pathJoin(location, "report.md")

    
    
    async function browse_folder() {
        try {
            [location] = await browse({dir:true})
            console.log(location)
            if(location) {
                reportFile = window.pathJoin(location, "report.md")
            }
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

    function openReport() {
        const reportContent = fs.existsSync(reportFile) ? fs.readFileSync(reportFile) : editor.getData()
        const reportHTML = `
        <div class="ck ck-editor__main ck-content content" 
            style="
            background: #fff; 
            padding: 1em;
            margin: 1em;
            user-select: text;
            ">
            ${window.marked(reportContent)}
        </div>
        `

        const graphWindow = new WinBox({
            root: document.getElementById("pageContainer"),
            title: `Report ${filetype} `,
            x: "center", y: "center",
            width: "70%", height: "70%",
            background:"#634e96",
            top: 50, bottom:50,
            html: reportHTML
        });
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
    .notification {width: 100%; border: 1px solid;}
    .editor-div * {color: black;}
</style>

<div class="align">

    <div class="title notification is-link">Report/Editor</div>
    <button class="button is-link" on:click="{browse_folder}">Browse</button>
    <button class="button is-link" on:click="{saveReport}">Save</button>

    <button class="button is-link" on:click="{()=>{
        console.log(window.marked(editor.getData()))
        openReport()
    }}">Show report</button>
    
</div>

<div class="ckeditor-svelte content" {id} use:mountEditor >
    {#if window.fs.existsSync(reportFile)}
        {@html window.marked(window.fs.readFileSync(reportFile))}
    {/if}
</div>