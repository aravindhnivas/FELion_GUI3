
<script>
    import {onMount, tick} from "svelte"
    export let id, title="Title", active=false;

    let graphWindowClosed = true;
    let graphWindow = null;

    // let maxHeight;
    // let buttonHeight=0, headerHeight=0;

    function openGraph(){

        if(!graphWindowClosed) {return graphWindow.show()}

        graphWindowClosed = false

        graphWindow = new WinBox({


            root:document.getElementById("pageContainer"), 
            mount: document.getElementById(id), title,
            x: "center", y: "center",
            width: "70%", height: "70%",
            background:"#634e96",
            top: 50, bottom:50,
            onclose: function(){
                graphWindowClosed = true
                active = false
                console.log(`graphWindowClosed: ${graphWindowClosed}`)
                return false
            },
            // onresize: function(width, height){maxHeight = height-buttonHeight-headerHeight-100},
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
        grid-template-rows: 3fr 12fr 1fr;
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

    {#if $$slots.footer_content__slot}

        <div class="footer_content" >

            <slot name="footer_content__slot"/> 
    
        </div>
    {/if}

</div>