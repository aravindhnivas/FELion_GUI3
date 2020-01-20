<script context="module">
    export const createToast = (msg, type="primary") => Toast.create({ message: msg, position:"is-top", type:`is-${type}`})
    export function browse({filetype="", dir=true}={}) {
        return new Promise((resolve, reject)=>{

            const mainWindow = remote.getCurrentWindow()
            let type;
            dir ? type = "openDirectory" : type = "openFile"

            const options = {
                filters: [
                    { name: filetype, extensions: [`*${filetype}`] },
                    { name: 'All Files', extensions: ['*'] }

                ],
                properties: [type, "multiSelections"],
            }
            remote.dialog.showOpenDialog(mainWindow, options)
            .then(result => {
                console.log(result.canceled)
                console.log(result.filePaths)
                resolve(result)
            }).catch(err => { 
                createToast("Couldn't open folder", "danger")
                reject(err) })
        })
    }

</script>

<script>
    
    // IMPORTING MODULES
    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';
    import IconButton, {Icon} from '@smui/icon-button';
    import { fly, slide } from 'svelte/transition';
    import Fab from '@smui/fab';
    import FormField from '@smui/form-field';
    import Switch from '@smui/switch';
    import Textfield from '@smui/textfield';
    import {onMount} from "svelte";
    import { Toast } from 'svelma'
    import {activated, modalContent, modalTitle} from "./Modal.svelte"
    ////////////////////////////////////////////////////////////////////////////

    // EXPORTED variables

    export let id;
    export let fileChecked=[];
    export let filetype = "felix"
    export let currentLocation = localStorage[`${filetype}_location`] || "";

    ////////////////////////////////////////////////////////////////////////////
    
    onMount(()=>{if (currentLocation != "") {getfiles()}})

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

        browse({dir:true}).then(result=>{
            if (!result.canceled) {
                localStorage[`${filetype}_location`] = currentLocation = result.filePaths[0]
                getfiles(true)

            }
        })
        
    }

    function getfiles(toast=false) {
        fileChecked = [], selectAll = false
        try {
            let folderfile = fs.readdirSync(currentLocation).map(file=>path.join(currentLocation, file))
            let allfiles = folderfile.filter(file=>fs.lstatSync(file).isFile())
            let typefiles = allfiles.filter(file=>file.endsWith(filetype))
            files = original_files = typefiles.map(file=>path.basename(file))
            otherfolders = folderfile.filter(file=>fs.lstatSync(file).isDirectory()).map(file=>path.basename(file))
            console.log("Folder updated for ", filetype, "\n", files)
            if (toast) {createToast("Files updated")}
        } catch (err) { 
            $modalContent = err;
            $activated = true;
         }

    }
    $: $activated ? console.log(`Modal activated for ${filetype}`) : console.log(`Modal deactivated for ${filetype}`)

    const changeDirectory = (goto) => {
        currentLocation = path.resolve(currentLocation, goto)
        getfiles()
    }

    let toggleBrowser = true;

</script>
<style lang="scss">

    $box1: #6a50ad59;
    .filebrowser, .fileContainer {
        background-image: url(./assets/css/intro.svg);
        height: calc(100vh - 7em);
    }

    .plotContainer {
        max-height: calc(100vh - 25em);
        overflow-y: auto;
        padding-bottom: 3em;
    }
     .filelist {
        max-height: calc(100vh - 30em);
        overflow-y: auto;
    }
    .folderfile-list {max-height: calc(100vh - 20em); overflow-y: auto;}
    
    .filebrowser {
        padding-left: 2em;
        padding-top: 1em;
        background-color: $box1;
        border-radius: 0;
        
    }

    .fileContainer {margin: 0 2em; padding-bottom: 5rem; width: calc(70vw - 2em)}
    
    * :global(.box){background-color: #654ca25c;}
    * :global(.mdc-list-item){height: 2em;}
    * :global(.mdc-switch.mdc-switch--checked .mdc-switch__thumb, .mdc-switch.mdc-switch--checked .mdc-switch__track){background-color: #ffffff}
    * :global(.material-icons) {margin-right:0.2em; cursor:pointer;}
    * :global(.align) { display: flex; align-items: center }
    * :global(.center) {justify-content: center;}
    * :global(.gap) {margin-right: 2em;}
    // * :global(.filebrowser) {flex:none; width:auto;}
    .buttonContainer {
        max-height: 20em;
        overflow-y: auto;
    }
    .box {border-radius: 0;}
    .container {min-height: calc(100vh - 10em);}
    .plotContainer > div {margin-top: 1em;}

</style>

<section {id} style="display:none" class="animated fadeIn">
    <div class="columns">

        {#if toggleBrowser}
            <div class="column is-one-fifth-widescreen is-one-quarter-desktop box filebrowser" transition:fly="{{ x: -20, duration: 500 }}">

                <div class="align center">
                    <Icon class="material-icons" on:click="{()=>changeDirectory(localStorage[`${filetype}_location`])}">home</Icon>
                    <Icon class="material-icons" on:click="{()=>{getfiles(true)}}">refresh</Icon>
                    <Icon class="material-icons" on:click="{()=>changeDirectory("../")}">arrow_back</Icon>
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
                            <div class="align" on:click="{()=>changeDirectory(folder)}" transition:slide|local>
                                <Icon class="material-icons">keyboard_arrow_right</Icon>
                                <div class="mdc-typography--subtitle1">{folder}</div>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>
        {/if}

        <div class="column fileContainer">
            <div class="container button-plot-container box">

                <div class="align">
                    <IconButton  toggle bind:pressed={toggleBrowser}>
                        <Icon class="material-icons" on>menu_open</Icon>
                        <Icon class="material-icons" >menu</Icon>
                    </IconButton>
                    <button class="button is-link gap" on:click={browse_folder}>Browse</button>
                    <Textfield on:change={getfiles} style="margin-bottom:1em;" bind:value={currentLocation} label="Current location" />
                </div>

                <div class="align buttonContainer"> <slot name="buttonContainer" /></div>
                <div class="plotContainer"> <slot name="plotContainer" /> </div>
                
            </div>
        </div>

    </div>
</section>