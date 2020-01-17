<script>
    
    // IMPORTING MODULES
    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';
    import IconButton, {Icon} from '@smui/icon-button';
    import { fly } from 'svelte/transition';
    import Fab from '@smui/fab';
    import FormField from '@smui/form-field';
    import Switch from '@smui/switch';
    import Textfield from '@smui/textfield';
    import {onMount} from "svelte";

    import { Toast } from 'svelma'

    ////////////////////////////////////////////////////////////////////////////

    // EXPORTED variables

    export let id;
    export let fileChecked=[];
    export let filetype = "felix"
    export let currentLocation = localStorage[`${filetype}_location`] || "";
    ////////////////////////////////////////////////////////////////////////////
    onMount(()=>{
        if (currentLocation != "") {getfiles()}
    })

    ////////////////////////////////////////////////////////////////////////////

    $: parentFolder = path.basename(currentLocation)
    let files = []
    let otherfolders = []
    let selectAll=false;
    let showfiles = true;
    let original_files = [];

    let searchKey = "";
    const searchfile = () => {
        console.log(searchKey)
        if (!searchKey) {files = original_files}
        else {files = original_files.filter(file=>file.includes(searchKey))}
    }

    function browse_folder() {
        let location = remote.dialog.showOpenDialogSync({ properties: ["openDirectory"] })
        location == undefined ? console.log("No files selected") : localStorage[`${filetype}_location`] = currentLocation = location[0]
        console.log(currentLocation)
        getfiles()
    }

    function getfiles(toast=false) {

        let folderfile = fs.readdirSync(currentLocation).map(file=>path.join(currentLocation, file))
        let allfiles = folderfile.filter(file=>fs.lstatSync(file).isFile())
        let typefiles = allfiles.filter(file=>file.includes(filetype))
        files = original_files = typefiles.map(file=>path.basename(file))
        otherfolders = folderfile.filter(file=>fs.lstatSync(file).isDirectory()).map(file=>path.basename(file))
        console.log("Folder updated for ", filetype, "\n", files)
        if (toast) Toast.create({ message: 'Files updated!', position:"is-top", type:"is-primary"})
    }

    const changeDirectory = (goto) => {
        currentLocation = path.join(currentLocation, goto);
        getfiles()
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

    // @media only screen
    // and (max-width: 1500px) {
    //     .filebrowser {width: 20%}
    // }

</style>

<section {id} style="display:none" >

    <div class="columns">

        <div class="column is-2 box filebrowser" >

            <div class="align center">
                <Icon class="material-icons" >home</Icon>
                <Icon class="material-icons" on:click="{()=>{getfiles(true)}}">refresh</Icon>
                <Icon class="material-icons" on:click="{()=>changeDirectory("..")}">arrow_back</Icon>
            </div>

            <Textfield on:keyup={searchfile} style="margin-bottom:1em;" bind:value={searchKey} label="Seach" />

            <div class="align center">
                <FormField>
                    <Switch bind:checked={selectAll} on:change="{()=>selectAll ? fileChecked = [...files] : fileChecked = []}"/>
                    <span slot="label">Select All</span>
                </FormField>
            </div>
            <div class="folderfile-list">

                <div class="align folderlist" >
                    <IconButton  toggle bind:pressed={showfiles}>
                        <Icon class="material-icons" on>keyboard_arrow_down</Icon>
                        <Icon class="material-icons" >keyboard_arrow_right</Icon>
                    </IconButton>
                    <div class="mdc-typography--subtitle1">{parentFolder}</div>
                </div>

                {#if showfiles && files != ""}
                    <div class="filelist" style="padding-left:1em;" transition:fly="{{ y: -20, duration: 500 }}">
                        <List checklist>
                            {#each files as file}
                                <Item>
                                    <Label>{file}</Label>
                                    <Meta> <Checkbox bind:group={fileChecked} value={file} on:click="{()=>selectAll=false}"/> </Meta>
                                </Item>
                            {/each}
                        </List>
                    </div>
                {:else if files == ""}
                    <div class="mdc-typography--subtitle1 align center">No {filetype} here!</div>        
                {/if}

                <div class="otherFolderlist" style="cursor:pointer">
                    {#each otherfolders as folder}
                        <div class="align" on:click="{()=>changeDirectory(folder)}">
                            <Icon class="material-icons">keyboard_arrow_right</Icon>
                            <div class="mdc-typography--subtitle1">{folder}</div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>

        <div class="column fileContainer">
            <div class="container box">
                <div class="align">
                    <button class="button is-link gap" on:click={browse_folder}>Browse</button>
                    <Textfield style="margin-bottom:1em;" bind:value={currentLocation} label="Current location" />
                </div>

                <div class="align buttonContainer"> <slot name="buttonContainer" /></div>
                <div class="align plotContainer"> <slot name="plotContainer" /> </div>
                
            </div>
        </div>

    </div>
</section>