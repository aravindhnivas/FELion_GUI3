
<script>
    import { slide } from 'svelte/transition';
    import CustomSwitch from '$components/CustomSwitch.svelte';
    import Textfield from '@smui/textfield';
    import {tick} from "svelte";
    import {onMount, afterUpdate} from "svelte"
    import CustomIconSwitch from '$components/CustomIconSwitch.svelte';
    import VirtualCheckList from '$components/VirtualCheckList.svelte';
    import { createEventDispatcher } from 'svelte';
    ///////////////////////////////////////////////////////////////////////////
    export let fileChecked = [],  currentLocation = "", filetype = "*.*", fullfileslist = [], markedFile = "";

    const dispatch = createEventDispatcher();

    let fullfiles = []
    function dispatch_chdir_event() { dispatch('chdir', { action: "chdir", filetype, currentLocation }) }

    let original_location = currentLocation
    let otherfolders = [], selectAll=false, showfiles = true, original_files = [];
    
    $: locationStatus = fs.existsSync(currentLocation)
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
            
            let folderfile = fs.readdirSync(currentLocation)
            const fileIncludePattern = new RegExp(`.+\\.[^fr]?${filetype}`) // f or r keyword is to avoid getting fscan and rscan files
            
            original_files = fullfiles = folderfile.filter(file=>fileIncludePattern.test(file)&&fs.lstatSync(pathJoin(currentLocation, file)).isFile()).map(file=>file={name:file, id:getID()}).sort((a,b)=>a.name<b.name?1:-1)

            fullfileslist = fullfiles.map(file=>file=file.name)
            otherfolders = folderfile.filter(file=>fs.lstatSync(pathJoin(currentLocation, file)).isDirectory()).map(file=>file={name:file, id:getID()}).sort((a,b)=>a.name>b.name?1:-1)
            
            original_location = currentLocation
            
            files_loaded = true;

            console.log("Folder updated");
            
            dispatch_chdir_event()
            if (filetype.length > 2) { db.set(`${filetype}_location`, currentLocation) }

            if (toast) { window.createToast("Files updated"); }
        } catch (error) {
            console.log(error)

            window.handleError(error)
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
            const _from = fullfileslist.indexOf(fileChecked.at(0))
            const _to = fullfileslist.indexOf(fileChecked.at(-1))
            if (_from < _to) {fileChecked = fullfileslist.slice(_from, _to+1)}
            else {fileChecked = fullfileslist.slice(_to, _from+1)}
        }

	}
</script>

<div class="align h-center">
    <i class="material-icons" on:click="{()=>changeDirectory("..")}">arrow_back</i>
    <i class="material-icons animated faster" 
        on:animationend={({target})=>target.classList.remove("rotateIn")} 
        on:click="{({target})=>{target.classList.add("rotateIn"); getfiles(true, true)}}">refresh</i>
    <CustomIconSwitch bind:toggler={sortFile} icons={["trending_up", "trending_down"]}/>
</div>

<Textfield on:keyup={searchfile} bind:value={searchKey} label="Search {filetype} files" />
<CustomSwitch  bind:selected={selectAll} label="Select All" 
    on:change="{()=>selectAll ? fileChecked = fullfiles.map(file=>file=file.name) : fileChecked = []}" />

<div id="{filetype}_filebrowser" style="width: 100%; overflow-y:auto;">
    <div class="align folderlist" >
        <i class="material-icons" >keyboard_arrow_right</i>
        <div>{parentFolder}</div>
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
            <div >No {filetype} here!</div>        
        {/if}
        
        <div style="cursor:pointer">
            {#each otherfolders as folder (folder.id)}
                <div class="align" on:click="{()=>changeDirectory(folder.name)}" transition:slide|local >
                    <i class="material-icons">keyboard_arrow_right</i>
                    <div class="mdc-typography--subtitle1">{folder.name}</div>
                </div>
            {/each}
        </div>

    {:else if !locationStatus}
        <div >Location doesn't exist: Browse files again</div>
    {:else}
        <div class="mdc-typography--subtitle1 align center">...loading</div>
    {/if}

</div>