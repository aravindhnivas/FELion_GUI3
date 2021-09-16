
<script>
    import {mainPreModal} from "../svelteWritable";
    import IconButton, {Icon} from '@smui/icon-button';

    import { slide } from 'svelte/transition';
    import FormField from '@smui/form-field';
    import Switch from '@smui/switch';

    import Textfield from '@smui/textfield';
    import {tick} from "svelte";
    import {onMount, afterUpdate} from "svelte"
    import CustomIconSwitch from './CustomIconSwitch.svelte';

    import VirtualCheckList from './VirtualCheckList.svelte';
    import { createEventDispatcher } from 'svelte';
    
    ///////////////////////////////////////////////////////////////////////////
    

    export let fileChecked = [],  currentLocation = "", filetype = "*.*", fullfileslist = [], markedFile = "";

    const dispatch = createEventDispatcher();

    let fullfiles = []

    // $: fullfileslist
    function dispatch_chdir_event() { dispatch('chdir', { action: "chdir", filetype, currentLocation }) }

    let original_location = currentLocation
    let otherfolders = [], selectAll=false, showfiles = true, original_files = [];
    $: locationStatus = existsSync(currentLocation)

    $: parentFolder = locationStatus ? basename(currentLocation) : "Undefined"

    let searchKey = "";
    
    const searchfile = () => {

        console.log(searchKey)
        if (!searchKey) {fullfiles = original_files}
        else {fullfiles = original_files.filter(file=>file.name.includes(searchKey))}

    }

    let files_loaded = false
    
    function getfiles(toast=false, keepfiles=false) {
    
        if (!locationStatus) {return window.createToast("Location undefined", "danger")}
        original_files = otherfolders = fullfiles = []

        if(!keepfiles){fileChecked = []}
        
        selectAll = files_loaded = false
        
        try {
            console.log("Current location: ", currentLocation)
            
            let folderfile = readdirSync(currentLocation)

            original_files = fullfiles = folderfile.filter(file=>file.endsWith(filetype)&&lstatSync(pathJoin(currentLocation, file)).isFile()).map(file=>file={name:file, id:getID()}).sort((a,b)=>a.name<b.name?1:-1)

            fullfileslist = fullfiles.map(file=>file=file.name)

            otherfolders = folderfile.filter(file=>lstatSync(pathJoin(currentLocation, file)).isDirectory()).map(file=>file={name:file, id:getID()}).sort((a,b)=>a.name>b.name?1:-1)
            
            original_location = currentLocation
            
            files_loaded = true;

            console.log("Folder updated");
            
            dispatch_chdir_event()
            if (filetype.length > 2) { db.set(`${filetype}_location`, currentLocation) }

            if (toast) { window.createToast("Files updated"); }
        } catch (error) {
            console.log(error)
            mainPreModal.error(error.stack || error)
            return 
        }
    }

    let sortFile = false
    $: sortFile ? fullfiles = fullfiles.sort((a,b)=>a.name>b.name?1:-1) : fullfiles = fullfiles.sort((a,b)=>a.name<b.name?1:-1)

    const changeDirectory = (goto) => { currentLocation = pathResolve(currentLocation, goto); getfiles() }

    onMount(()=> {if(locationStatus) {getfiles(); console.log("onMount Updating location for ", filetype)}} )
    afterUpdate(() => {
        
        if (original_location !== currentLocation && locationStatus) {

            getfiles(true); console.log("Updating location for ", filetype)
        }

    });

    async function selectRange(event) {

        await tick();
        if (event.shiftKey && fileChecked.length) {
            const _from = window._.indexOf(fullfileslist, fileChecked[0])
            const _to = window._.indexOf(fullfileslist, fileChecked.slice(fileChecked.length-1)[0])
            if (_from < _to) {fileChecked = fullfileslist.slice(_from, _to+1)}
            else {fileChecked = fullfileslist.slice(_to, _from+1)}
        }

	}

    // let markedFile = ""

</script>

<style>
    .folderfile-list {max-height: calc(100vh - 20em); overflow-y: auto;}
    .align {display: flex; align-items: center;}
    .center {justify-content: center;}
    .browseIcons {cursor: pointer;}
</style>


<div class="align center browseIcons">
    <Icon class="material-icons" on:click="{()=>changeDirectory("..")}">arrow_back</Icon>
    <Icon class="material-icons" on:click="{()=>{getfiles(true, true)}}">refresh</Icon>
    <CustomIconSwitch bind:toggler={sortFile} icons={["trending_up", "trending_down"]}/>

</div>

<Textfield on:keyup={searchfile} style="margin-bottom:1em; width:100%; " bind:value={searchKey} label="Seach" />
<div class="align center">
    <FormField>
    
        <Switch bind:checked={selectAll} on:change="{()=>selectAll ? fileChecked = fullfiles.map(file=>file=file.name) : fileChecked = []}"/>
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

    {#if files_loaded && locationStatus}
        {#if showfiles && fullfiles.length }
            <div on:click={selectRange}>
                <VirtualCheckList bind:fileChecked bind:items={fullfiles} {markedFile} on:click="{(e)=>{
                    selectAll=false;
                    if(e.ctrlKey && filetype.includes("felix") ) { markedFile = e.target.value; dispatch('markedFile', {  markedFile })}
                }}" on:select="{(e)=>console.log(e)}"/>

            </div>
        {:else if fullfiles.length <= 0}
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