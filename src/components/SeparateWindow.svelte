
<script>
    import {onMount, tick} from "svelte"
    export let id=window.getID(), title="Title", active=false;
    export let top=50, bottom=50;
    export let width="70%", height="70%";
    export let x="center", y="center";

    export let background="#634e96";
    
    let graphWindowClosed = true;
    let graphWindow = null;

    function openGraph(){

        if(!graphWindowClosed) {return graphWindow.show()}
        graphWindowClosed = false
        graphWindow = new WinBox({

            root:document.getElementById("pageContainer"),


            mount: document.getElementById(id), 
            title, x, y, width, height, top, bottom, background,
            
            onclose: function(){
                graphWindowClosed = true
                active = false
                console.log(`graphWindowClosed: ${graphWindowClosed}`)
                return false
            },
        });
    }
    onMount(async ()=> {
    
        await tick(); openGraph()
    
    })

</script>


<style>

    .main_content {
        overflow: auto;
    }

    .main_content__div {
        display:grid;
        /* grid-template-rows: 3fr 12fr 1fr; */
        grid-template-rows: auto 1fr auto;
        max-height: 100%;
        padding: 1em;
    }

    .header_content {

        display:grid;

        grid-row-gap: 1em;
    }

    .footer_content {
        display: grid;
        grid-auto-flow: column;

        grid-auto-columns: max-content;
        
        margin-left: auto;
    }

</style>

<div {id} class="main_content__div">

    <div class="header_content"><slot name="header_content__slot" /></div>
    <div class="main_content"><slot name="main_content__slot" /></div>
    <div class="footer_content" ><slot name="footer_content__slot"/> </div>
    
</div>