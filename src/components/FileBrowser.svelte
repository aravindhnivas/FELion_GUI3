<script context="module">
    export const createToast = (msg, type="primary") => Toast.create({ message: msg, position:"is-top", type:`is-${type}`})
</script>

<script>

    import IconButton, {Icon} from '@smui/icon-button';

    import { slide } from 'svelte/transition';
    import FormField from '@smui/form-field';
    import Switch from '@smui/switch';
    import Textfield from '@smui/textfield';
    
    import { Toast } from 'svelma'
    
    import {onMount, afterUpdate} from "svelte"
    
    import CustomIconSwitch from './CustomIconSwitch.svelte';
    import CustomCheckList from './CustomCheckList.svelte';
    import { createEventDispatcher } from 'svelte';
    import PreModal from "./PreModal.svelte";
    
    ///////////////////////////////////////////////////////////////////////////

    export let fileChecked = [],  currentLocation = "", filetype = "*.*"

    const dispatch = createEventDispatcher();

    let preModal = {};

    function dispatch_chdir_event() { dispatch('chdir', { action: "chdir", filetype, currentLocation }) }

    let original_location = currentLocation
    let files = [], otherfolders = [], selectAll=false, showfiles = true, original_files = [];
    $: parentFolder = fs.existsSync(currentLocation) ? path.basename(currentLocation) : "Undefined"

    $: locationStatus = fs.existsSync(currentLocation) ? true : false

    let searchKey = "";
    const searchfile = () => {
        console.log(searchKey)
        if (!searchKey) {files = original_files}
        else {files = original_files.filter(file=>file.name.includes(searchKey))}
    }

    let files_loaded = false
    function getfiles(toast=false) {
        if (fs.existsSync(currentLocation)) {original_files = otherfolders = files = fileChecked = [], selectAll = files_loaded = false}
        else {return createToast("Location undefined", "danger")}
        try {

            console.log("Current location: ", currentLocation)
            
            let folderfile = fs.readdirSync(currentLocation)
            original_files = files = folderfile.filter(file=>file.endsWith(filetype)&&fs.lstatSync(path.join(currentLocation, file)).isFile()).map(file=>file={name:file, id:getID()}).sort((a,b)=>a.name<b.name?1:-1)

            otherfolders = folderfile.filter(file=>fs.lstatSync(path.join(currentLocation, file)).isDirectory()).map(file=>file={name:file, id:getID()}).sort((a,b)=>a.name>b.name?1:-1)
            
            original_location = currentLocation
            
            files_loaded = true
            console.log("Folder updated");
            dispatch_chdir_event()
            
            if (toast) {createToast("Files updated")}
        } catch (err) {
            console.log(err)
            preModal.modalContent = err;
            preModal.open = true;
            return original_files = otherfolders = files = fileChecked = []
        }
    }

    let sortFile = false
    $: sortFile ? files = files.sort((a,b)=>a.name>b.name?1:-1) : files = files.sort((a,b)=>a.name<b.name?1:-1)
    const changeDirectory = (goto) => {

        if (!fs.existsSync(currentLocation)) {return createToast("Location undefined", "danger")}
        currentLocation = path.resolve(currentLocation, goto)

        getfiles()
    }

    onMount(()=> {if(fs.existsSync(currentLocation)) {getfiles(); console.log("onMount Updating location for ", filetype)}} )
    afterUpdate(() => {
        if (original_location !== currentLocation) {
            if(fs.existsSync(currentLocation)) {getfiles(); console.log("Updating location for ", filetype)}
            else {return createToast("Location undefined", "danger")}
        
        }
    });
</script>

<style>

    /* .filelist { max-height: calc(100vh - 30em); overflow-y: auto; } */
    .folderfile-list {max-height: calc(100vh - 20em); overflow-y: auto;}
    .align {display: flex; align-items: center;}
    .center {justify-content: center;}
    .browseIcons {cursor: pointer;}
</style>
<PreModal bind:preModal/>
<div class="align center browseIcons">
    <Icon class="material-icons" on:click="{()=>changeDirectory("..")}">arrow_back</Icon>
    <Icon class="material-icons" on:click="{()=>{getfiles(true)}}">refresh</Icon>
    <CustomIconSwitch bind:toggler={sortFile} icons={["trending_up", "trending_down"]}/>
</div>

<Textfield on:keyup={searchfile} style="margin-bottom:1em;" bind:value={searchKey} label="Seach" />
<div class="align center">
    <FormField>
        <Switch bind:checked={selectAll} on:change="{()=>selectAll ? fileChecked = files.map(file=>file=file.name) : fileChecked = []}"/>
        <span slot="label">Select All</span>
    </FormField>
</div>

<div class="folderfile-list" id="{filetype}_filebrowser">
    <div class="align folderlist" >
        <IconButton  toggle bind:pressed={showfiles}>

            <Icon class="material-icons" on>keyboard_arrow_down</Icon>
            <Icon class="material-icons" >keyboard_arrow_right</Icon>
        </IconButton>

        <div class="mdc-typography--subtitle1">{parentFolder}</div>

    </div>
    {#if files_loaded}
        {#if showfiles && files != "" }
            <CustomCheckList bind:fileChecked bind:items={files} on:click="{()=>selectAll=false}"/>
        {:else if files == ""}
            <div class="mdc-typography--subtitle1 align center">No {filetype} here!</div>        
        {/if}
        <div class="otherFolderlist" style="cursor:pointer">
            {#each otherfolders as folder (folder.id)}
                <div class="align" on:click="{()=>changeDirectory(folder.name)}" transition:slide|local>
                    <Icon class="material-icons">keyboard_arrow_right</Icon>
                    <div class="mdc-typography--subtitle1">{folder.name}</div>
                </div>
            {/each}
        </div>
    {:else if !locationStatus}

        <div class="mdc-typography--subtitle1 align center">Location doesn't exist: Browse files again</div>
    {:else}
        <div class="mdc-typography--subtitle1 align center">...loading</div>
    
    {/if}

</div>