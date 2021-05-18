
<script>
    import {onMount, tick} from "svelte"
    export let id, title="Title", active=false;

    let graphWindowClosed = true;
    let graphWindow = null;

    let maxHeight;
    let buttonHeight=0;

    function openGraph(){

        if(!graphWindowClosed) {
            return graphWindow.show()
        }

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

            onresize: function(width, height){

                maxHeight = height-buttonHeight-50

            },
        });
    }
    

    onMount(async ()=> {

        await tick()
        openGraph()

    })
</script>


<style>
    .main_content {
        overflow: auto;
        padding: 1em;

    }

    .main_content__div {

        display:grid;

        grid-template-rows: 1fr auto;
    }

</style>

<div {id} class="main_content__div">

    <div  style="max-height: {maxHeight}px;" class="main_content"><slot name="content" /></div>

    {#if $$slots.footerbtn}
        <div style="margin-left:auto; display:flex;" bind:clientHeight={buttonHeight}>
        
            <slot name="footerbtn"/> 

        </div>
    
    {/if}

</div>