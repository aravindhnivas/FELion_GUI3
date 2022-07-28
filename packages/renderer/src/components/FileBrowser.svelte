<script lang="ts">
    import { onMount, afterUpdate, createEventDispatcher } from 'svelte'
    import { slide } from 'svelte/transition'
    import Textfield from '@smui/textfield'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import CustomIconSwitch from '$components/CustomIconSwitch.svelte'
    import VirtualCheckList from '$components/VirtualCheckList.svelte'
    export let filetype = '*.*'
    export let markedFile = ''
    export let fileChecked = []
    export let fullfileslist = []
    export let currentLocation = ''

    ///////////////////////////////////////////////////////////////////////////

    const dispatch = createEventDispatcher()

    let fullfiles = []
    // function dispatch_chdir_event() { dispatch('chdir', { action: "chdir", filetype, currentLocation }) }

    let selectAll = false
    let otherfolders = []
    let original_files = []

    $: locationStatus = window.fs.isDirectory(currentLocation)
    $: parentFolder = locationStatus ? window.path.basename(currentLocation) : 'Undefined'

    let searchKey = ''
    const searchfile = () => {
        console.log(searchKey)
        if (!searchKey) {
            fullfiles = original_files
        } else {
            fullfiles = original_files.filter((file) => file.name.includes(searchKey))
        }
    }
    let filesLoaded = false
    function getfiles(toast = false, keepfiles = false) {
        return new Promise(async (resolve, reject) => {
            if (!locationStatus) {
                reject("Location doesn't exist: Browse files again")
                if (!toast) return
                return window.createToast('Location undefined', 'danger')
            }

            original_files = otherfolders = fullfiles = []
            if (!keepfiles) {
                fileChecked = []
            }
            selectAll = false
            filesLoaded = false

            try {
                const folderfile = await window.fs.readdir(currentLocation)
                if (window.fs.isError(folderfile)) {
                    throw folderfile
                }

                const fileIncludePattern = new RegExp(`.+\\.[^fr]?${filetype}`) // f or r keyword is to avoid getting fscan and rscan files

                original_files = fullfiles = folderfile
                    .filter(
                        (file) =>
                            fileIncludePattern.test(file) && window.fs.isFile(window.path.join(currentLocation, file))
                    )
                    .map((file) => (file = { name: file, id: window.getID() }))
                    .sort((a, b) => (a.name < b.name ? 1 : -1))

                fullfileslist = fullfiles.map((file) => (file = file.name))
                otherfolders = folderfile
                    .filter((file) => window.fs.isDirectory(window.path.join(currentLocation, file)))
                    .map((file) => (file = { name: file, id: window.getID() }))
                    .sort((a, b) => (a.name > b.name ? 1 : -1))

                console.log('Folder updated')

                original_location = currentLocation
                dispatch('chdir', {
                    action: 'chdir',
                    filetype,
                    currentLocation,
                    fullfileslist,
                })

                if (filetype.length > 2) {
                    window.db.set(`${filetype}_location`, currentLocation)
                }
                filesLoaded = true
                resolve(fullfiles)
            } catch (error) {
                reject(error)
                window.handleError(error)
            }
        })
    }

    let sortFile = false
    $: sortFile
        ? (fullfiles = fullfiles.sort((a, b) => (a.name > b.name ? 1 : -1)))
        : (fullfiles = fullfiles.sort((a, b) => (a.name < b.name ? 1 : -1)))
    let getFilePromise
    const changeDirectory = (goto) => {
        currentLocation = window.path.resolve(currentLocation, goto)
    }

    let original_location = currentLocation
    const updateFiles = async () => {
        if (locationStatus) {
            getFilePromise = await getfiles()
            console.log('Updating files for ', filetype)
        }
    }

    let mounted = false
    onMount(async () => {
        await updateFiles()
        mounted = true
    })

    afterUpdate(() => {
        if (original_location !== currentLocation) {
            updateFiles()
        }
    })

    $: if (currentLocation) {
        fileChecked = []
    }

    const get_marked_file = (e) => {
        selectAll = false
        if (!(e.ctrlKey && filetype.includes('felix'))) return

        const filename = e.target.value
        markedFile = markedFile === filename ? '' : filename

        dispatch('markedFile', { markedFile })
    }
    $: fileSelected = fileChecked
</script>

<div class="filebrowser-header">
    <div class="align h-center">
        <i class="material-symbols-outlined" on:click={() => changeDirectory('..')}>arrow_back</i>

        <i
            class="material-symbols-outlined animate__animated animate__faster"
            on:animationend={({ target }) => target.classList.remove('animate__rotateIn')}
            on:click={({ target }) => {
                target.classList.add('animate__rotateIn')
                getFilePromise = getfiles(true, true)
            }}>refresh</i
        >

        <CustomIconSwitch bind:toggler={sortFile} icons={['trending_up', 'trending_down']} />
    </div>

    <Textfield on:keyup={searchfile} bind:value={searchKey} label="Search {filetype} files" />
    <CustomSwitch
        bind:selected={selectAll}
        label="Select All"
        on:change={() => {
            console.log('selected all files')
            selectAll ? (fileChecked = fullfiles.map((file) => (file = file.name))) : (fileChecked = [])
        }}
    />
</div>

<div
    class="main__container"
    id="{filetype}_filebrowser"
    style:grid-template-rows={fullfiles.length
        ? otherfolders.length
            ? 'auto 4fr 0.5fr'
            : 'auto 1fr'
        : otherfolders.length
        ? 'auto auto 1fr'
        : 'auto 1fr'}
>
    <div class="align file-dir">
        <i class="material-symbols-outlined">keyboard_arrow_right</i>
        <div>{parentFolder}</div>
    </div>

    {#await getFilePromise}
        <div class="mdc-typography--subtitle1 align center">...loading</div>
    {:then value}
        {#if fullfiles.length && mounted}
            <VirtualCheckList
                class="files"
                on:fileselect
                bind:fileChecked
                {fileSelected}
                items={fullfiles}
                {markedFile}
                on:click={get_marked_file}
            />
        {:else if fullfiles.length <= 0}
            <div>No {filetype} here! or try reload files</div>
        {/if}
        {#if otherfolders.length}
            <div class="folders">
                {#each otherfolders as folder (folder.id)}
                    <div class="align" on:click={() => changeDirectory(folder.name)} transition:slide|local>
                        <i class="material-symbols-outlined">keyboard_arrow_right</i>
                        <div class="folder mdc-typography--subtitle1">{folder.name}</div>
                    </div>
                {/each}
            </div>
        {/if}
    {:catch error}
        <div>{error}</div>
    {/await}
</div>

<style>
    .filebrowser-header {
        display: flex;
        flex-direction: column;
        gap: 0.5em;
    }
    .main__container {
        width: 100%;
        display: grid;
        grid-auto-flow: row;
        overflow-y: hidden;
        gap: 1em;
    }

    .folder {
        cursor: pointer;
    }
    .folders {
        overflow-y: auto;
    }
</style>
