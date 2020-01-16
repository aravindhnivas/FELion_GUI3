<script>
    import Ripple from '@smui/ripple';
    import {onMount, onDestroy} from "svelte";
    import LoremIpsum from "../testing/LoremIpsum.svelte"
    export let id;

    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';

    let fileChecked;
    let folderfile = ["File1", "File2", "File3", "File4"]
    $: console.log(fileChecked)

    onMount(()=>fileChecked=[])
</script>


<style lang="scss">

    // Variables
    $box1: #6a50ad59;

    .filebrowser, .fileContainer {
        background-image: url(./assets/css/intro.svg);
        height: calc(100vh - 8em);
        overflow-y: auto;
    }

    .filebrowser {
        padding-left: 2em;
        padding-top: 1em;
        background-color: $box1;
    }

    .container {padding: 5em;}
    hr {margin: 1em 0;}

    h1 {
        font-weight: 300;
    }

    * :global(.mdc-list-item){height: 2em;}

</style>

<section {id} style="display:none" >

    <div class="columns">

        <div class="column is-2 box filebrowser" >
            <div use:Ripple={[true, {color: 'surface'}]} tabindex="0"><h1 >FILE EXPLORER</h1></div>
            <hr>
            <div class="">
                <List class="demo-list" checklist>
                    {#each folderfile as file}
                        <Item>
                            <Label>{file}</Label>
                            <Meta> <Checkbox bind:group={fileChecked} value={file} /> </Meta>
                        </Item>
                    {/each}
                </List>
            </div>
        </div>


        <div class="column fileContainer">
            <div class="container box">
                <h1>{id}</h1>
                <hr>
                
            </div>
        </div>

    </div>
</section>