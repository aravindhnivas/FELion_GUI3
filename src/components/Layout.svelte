<script>
    import Ripple from '@smui/ripple';
    import {onMount, afterUpdate} from "svelte";
    import LoremIpsum from "../testing/LoremIpsum.svelte"
    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';
    import IconButton, {Icon} from '@smui/icon-button';

    import Fab from '@smui/fab';
    import FormField from '@smui/form-field';
    import Switch from '@smui/switch';
    import Textfield from '@smui/textfield'
    export let id;

    export let fileChecked=[];
    export let currentLocation = localStorage["currentLocation"] || "";

    let folderfile = ["File1", "File2", "File3", "File4"]

    let selectAll=false;

    let searchKey = "";
    const searchfile = () => {
        console.log(searchKey)
        if (!searchKey) {folderfile = ["File1", "File2", "File3", "File4"]}
        else {folderfile = folderfile.filter(file=>file.includes(searchKey))}
    }

    // Browse file
    function browse_folder() {
        let location = remote.dialog.showOpenDialogSync({ properties: ["openDirectory"] })
        location == undefined ? console.log("No files selected") : localStorage["currentLocation"] = currentLocation = location[0]
        console.log(currentLocation)
    }
    

</script>

<style lang="scss">

    $box1: #6a50ad59;

    .filebrowser, .fileContainer {
        background-image: url(./assets/css/intro.svg);
        height: calc(100vh - 7em);
    }
    .plotContainer {
        max-height: calc(100vh - 21em);
        overflow-y: auto;
    }
     .filelist {
        max-height: calc(100vh - 30em);
        overflow-y: auto;
    
    }

    .plotContainer, .filelist, .otherFolderlist {padding-bottom: 5em}
    .folderfile-list {max-height: calc(100vh - 20em); overflow-y: auto;}
    
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
    .fileContainer {margin: 0 2em; padding-bottom: 5rem;}
    .gap {margin-right: 2em;}

    * :global(.box){background-color: #654ca25c;}

    * :global(.mdc-list-item){height: 2em;}
    * :global(.mdc-switch.mdc-switch--checked .mdc-switch__thumb, .mdc-switch.mdc-switch--checked .mdc-switch__track){background-color: #ffffff}

    .buttonContainer {
        max-height: 6em;
        overflow-y: auto;
        padding: 2em 0;
    }
    .box {border-radius: 0;}

    * :global(.material-icons) {margin-right:0.2em; cursor:pointer;}

</style>

<section {id} style="display:none" >

    <div class="columns">

        <div class="column is-2 box filebrowser" >

            <div class="align center">
                <Icon class="material-icons" >home</Icon>
                <Icon class="material-icons" >refresh</Icon>
                <Icon class="material-icons" >arrow_back</Icon>
            </div>

            <Textfield on:keyup={searchfile} style="margin-bottom:1em;" bind:value={searchKey} label="Seach" />

            <div class="align center">
                <FormField>
                    <Switch bind:checked={selectAll} on:change="{()=>selectAll ? fileChecked = [...folderfile] : fileChecked = []}"/>
                    <span slot="label">Select All</span>
                </FormField>
            </div>
            <div class="folderfile-list">

                <div class="align folderlist" >
                    <IconButton  toggle on:click="{()=>window.togglepage("Folder1")}">
                        <Icon class="material-icons">keyboard_arrow_down</Icon>
                        <Icon class="material-icons" on>keyboard_arrow_right</Icon>
                    </IconButton>
                    <div class="mdc-typography--subtitle1">Folder1</div>
                </div>

                <div class="filelist" style="padding-left:1em;"  id="Folder1" >

                    <List checklist>
                        {#each folderfile as file}
                            <Item >
                                <Label>{file}</Label>
                                <Meta> <Checkbox bind:group={fileChecked} value={file} on:click="{()=>selectAll=false}"/> </Meta>
                            </Item>
                        {/each}
                    </List>
                </div>

                <div class="otherFolderlist">
                    <div class="folders"></div>
                </div>
            </div>
        </div>

        <div class="column fileContainer">
            <div class="container box">
                <div class="align">
                    <button class="button is-link gap" on:click={browse_folder}>Browse</button>
                    <Textfield style="margin-bottom:1em;" bind:value={currentLocation} label="Current location" />
                </div>

                <div class="align buttonContainer"> <div class="mdc-typography--heading5">buttonContainer</div> </div>
                <div class="align plotContainer"> <div class="mdc-typography--heading5">plotContainer</div> </div>
                
            </div>
        </div>

    </div>
</section>