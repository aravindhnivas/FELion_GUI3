
<script>
    import {tick} from "svelte"
    export let id=window.getID(), title="Title", active=false;
    export let top=50, bottom=50;
    export let width="70%", height="70%";
    export let x="center", y="center";

    export let background="#634e96";
    
    export let graphWindow=null, windowReady=false;
    let graphWindowClosed = true;

    async function openGraph(){
        
        await tick()
        if(!graphWindowClosed) {return graphWindow.show()}
        graphWindowClosed = false


        graphWindow = new WinBox({
            root:document.getElementById("pageContainer"),
            mount: document.getElementById(id), 
            title, x, y, width, height, top, bottom, background,
            onclose: function(){
                graphWindowClosed = true
                active = false
                windowReady = false
                console.log(`graphWindowClosed: ${graphWindowClosed}`)
                return false
            },
            onfocus: function(){windowReady = true;console.log(windowReady, graphWindow)}
        });
    }

</script>

<style>

    .main_content {overflow: auto; margin-bottom: 1em;}
    .main_content__div {
        display:grid;


        grid-template-rows: auto 1fr auto;

        max-height: 100%;
        padding: 1em;

    }
    .header_content { display:grid; grid-row-gap: 1em; }
    .footer_content {margin-left: auto;}

</style>

<div {id} class="main_content__div" use:openGraph>
    <div class="header_content"><slot name="header_content__slot" /></div>

    <div class="main_content"><slot name="main_content__slot" /></div>
    <div class="footer_content" ><slot name="footer_content__slot"/> </div>
</div>