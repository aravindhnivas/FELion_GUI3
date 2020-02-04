<script context="module">
    export const createToast = (msg, type="primary") => Toast.create({ message: msg, position:"is-top", type:`is-${type}`})
</script>

<script>

    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';
    import IconButton, {Icon} from '@smui/icon-button';
    import { fly, slide } from 'svelte/transition';
    import FormField from '@smui/form-field';
    import Switch from '@smui/switch';

    import Textfield from '@smui/textfield';
    import { Toast } from 'svelma'
    import {activated, modalContent, modalTitle} from "./Modal.svelte"
    
    import {onMount, afterUpdate, beforeUpdate} from "svelte"
    const tree = require("directory-tree")
    // console.log(tree)
    ///////////////////////////////////////////////////////////////////////////

    export let fileChecked = [],  currentLocation = "", filetype = ""

    let original_location = currentLocation
    let files = [], otherfolders = [], selectAll=false, showfiles = true, original_files = [];
    let searchKey = "";

    $: parentFolder = path.basename(currentLocation)

    const searchfile = () => {
        console.log(searchKey)
        if (!searchKey) {files = original_files}
        else {files = original_files.filter(file=>file.includes(searchKey))}

    }

    function getfiles(toast=false) {

        original_files = otherfolders = files = fileChecked = [], selectAll = false
        try {
            console.log("Current location: ", currentLocation)
            let folderfile = tree( currentLocation, { extensions: new RegExp(filetype) } )
            
            original_files = files = folderfile.children.filter(file => file.type === "file").map(file=>file.name)

            otherfolders = folderfile.children.filter(file => file.type === "directory").map(file=>file.name)
            console.log(folderfile)
            
            original_location = currentLocation
            
            console.log("Folder updated");
            if (toast) {createToast("Files updated")}

        } catch (err) {
            console.log(err)
            $modalContent = err;
            $activated = true;
        }

    }

    const changeDirectory = (goto) => {

        currentLocation = path.resolve(currentLocation, goto)
        getfiles()
    }
    onMount(()=> {if(currentLocation !== "") {getfiles(); console.log("onMount Updating location for ", filetype)}} )

    afterUpdate(() => {
        if (original_location !== currentLocation) {getfiles(); console.log("Updating location for ", filetype)}
    });
</script>

<style>

    .filelist { max-height: calc(100vh - 30em); overflow-y: auto; }
    .folderfile-list {max-height: calc(100vh - 20em); overflow-y: auto;}

    .align {display: flex; align-items: center;}
    .center {justify-content: center;}
    .browseIcons {cursor: pointer;}

</style>

<div class="align center browseIcons">
    <Icon class="material-icons" on:click="{()=>changeDirectory(original_location)}">home</Icon>
    
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


    {#if showfiles && files != "" }
        <div class="filelist" style="padding-left:1em;" transition:fly="{{ y: -20, duration: 500 }}">

            <List checklist>

                {#each files as file (file)}
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
        {#each otherfolders as folder (folder)}
            <div class="align" on:click="{()=>changeDirectory(folder)}" transition:slide|local>
                <Icon class="material-icons">keyboard_arrow_right</Icon>
                <div class="mdc-typography--subtitle1">{folder}</div>
            </div>
        {/each}
    </div>
</div>
