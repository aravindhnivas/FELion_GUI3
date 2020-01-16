<script>
    import Ripple from '@smui/ripple';
    import {onMount, afterUpdate} from "svelte";
    import LoremIpsum from "../testing/LoremIpsum.svelte"
    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';
    import IconButton, {Icon} from '@smui/icon-button';

    export let id;

    let fileChecked=[];
    let folderfile = ["File1", "File2", "File3", "File4"]

    // $: console.log(fileChecked)
    // onMount(()=>fileChecked=[])
    afterUpdate(() => { console.log(fileChecked) });

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
            <div class="content" use:Ripple={[true, {color: 'surface'}]} tabindex="0" >
                <Icon class="material-icons is-pulled-left" style="margin-right:0.2em">folder_open</Icon>
                <h1 class="mdc-typography--headline5 ">FILE EXPLORER</h1>
            </div>
            <hr>
            <div>
                <List checklist>
                    {#each folderfile as file}
                        <Item>
                            <Label>{file}</Label>
                            <Meta> <Checkbox bind:group={fileChecked} value={file} /> </Meta>
                        </Item>
                    {/each}
                </List>
            </div>
        </div>

        <!-- {@debug fileChecked} -->
        <div class="column fileContainer">
            <div class="container box">
                <h1>{id}</h1>
                <hr>
                
            </div>
        </div>

    </div>
</section>