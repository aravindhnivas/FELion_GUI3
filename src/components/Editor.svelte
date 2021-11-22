<script>
    // import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
    import ClassicEditor from '$static/assets/js/ckeditor5';
    export let id = window.getID();
    export let editor;
    async function mountEditor(node) {
        try {
            editor = await ClassicEditor.create( node, {toolbar: {shouldNotGroupWhenFull: true}})
        } catch (error) {window.handleError( error );}
        return {destroy() {editor.destroy().catch(window.handleError)} }

    }

    function openReport() {
        const graphWindow = new WinBox({
            root: document.getElementById("pageContainer"),
            title: `Report`,
            x: "center", y: "center",
            width: "70%", height: "70%",
            background:"#634e96",
            top: 50, bottom:50,
            html: `
                <div class="ck ck-editor__main ck-content content" 
                    style="
                    background: #fff; 
                    padding: 1em;
                    margin: 1em;
                    user-select: text;
                    ">
                    ${window.marked(editor.getData())}
                </div>
            `
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
    <button class="button is-link" on:click="{()=>{
        console.log(window.marked(editor.getData()))
        openReport()
    }}">Export to HTML</button>
</div>

<div class="ckeditor-svelte content" {id} use:mountEditor>
    <h1 id="here-goes-the-initial-content-of-the-editor">Here goes the initial content of the editor.</h1>
    <p>code</p>
    <ul>
    <li>123</li>
    <li>456</li>
    <li>789</li>
    </ul>
    <p><code>code</code></p>
    <pre><code class="language-plaintext">code</code></pre>
</div>