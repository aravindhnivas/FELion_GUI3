<script>
    import Ripple from '@smui/ripple';
    import {onMount, afterUpdate} from "svelte";
    import LoremIpsum from "../testing/LoremIpsum.svelte"
    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';
    import IconButton, {Icon} from '@smui/icon-button';

    import FormField from '@smui/form-field';
    import Switch from '@smui/switch';
    import Textfield from '@smui/textfield'
    export let id;

    let folderfile = ["File1", "File2", "File3", "File4"]
    let fileChecked=[];
    let selectAll=false;

    let searchKey = "";
    const searchfile = () => {
        console.log(searchKey)
        if (!searchKey) {folderfile = ["File1", "File2", "File3", "File4"]}
        else {folderfile = folderfile.filter(file=>file.includes(searchKey))}
    }
    
</script>

<style lang="scss">

    // Variables
    $box1: #6a50ad59;

    .filebrowser, .fileContainer {
        background-image: url(./assets/css/intro.svg);
        height: calc(100vh - 8em);
        overflow-y: auto;
    }

    .align {

        display: flex;
        align-items: center;
    }
    .center {justify-content: center;}

    .filebrowser {
        padding-left: 2em;
        padding-top: 1em;
        background-color: $box1;
        border-radius: 0;

    }

    .container {padding: 5em;}
    hr {margin: 1em 0;}

    h1 {
        font-weight: 300;
    }

    * :global(.mdc-list-item){height: 2em;}
    * :global(.mdc-switch.mdc-switch--checked .mdc-switch__thumb, .mdc-switch.mdc-switch--checked .mdc-switch__track){background-color: #ffffff}
</style>

<section {id} style="display:none" >
    <div class="columns">

        <div class="column is-2 box filebrowser" >

            <div class="align center">
                <Icon class="material-icons" style="margin-right:0.2em; cursor:pointer;">home</Icon>
                <Icon class="material-icons" style="margin-right:0.2em; cursor:pointer;">refresh</Icon>
                <Icon class="material-icons" style="margin-right:0.2em; cursor:pointer;">arrow_back</Icon>
            </div>

            <!-- <hr> -->
            <Textfield on:keyup={searchfile} style="margin-bottom:1em;" bind:value={searchKey} label="Seach" />

            <div class="align center">
                <FormField>
                    <Switch bind:checked={selectAll} on:change="{()=>selectAll ? fileChecked = [...folderfile] : fileChecked = []}"/>
                    <span slot="label">Select All</span>
                </FormField>
            </div>

            <div class="align" >
                <IconButton  toggle on:click="{()=>window.togglepage("Folder1")}">
                    <Icon class="material-icons">keyboard_arrow_down</Icon>
                    <Icon class="material-icons" on>keyboard_arrow_right</Icon>
                </IconButton>
                <div class="mdc-typography--subtitle1">Folder1</div>
            </div>

            <div style="padding-left:1em;" id="Folder1" >
                <List checklist>
                    {#each folderfile as file}
                        <Item >
                            <Label>{file}</Label>
                            <Meta> <Checkbox bind:group={fileChecked} value={file} on:click="{()=>selectAll=false}"/> </Meta>
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