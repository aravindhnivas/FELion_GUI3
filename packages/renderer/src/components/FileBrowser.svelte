<script lang="ts">
    import { slide } from 'svelte/transition'
    import Textfield from '@smui/textfield'
    import MenuSurface from '@smui/menu-surface'
    import CustomIconSwitch from '$components/CustomIconSwitch.svelte'
    import VirtualCheckList from '$components/VirtualCheckList.svelte'
    export let filetype = '*.*'
    export let markedFile = ''
    export let fileChecked = []
    export let fullfileslist = []
    export let currentLocation = ''
    ///////////////////////////////////////////////////////////////////////////

    const dispatch = createEventDispatcher()
    let searchSurface = null
    let fullfiles = []
    let selectAll = false
    let otherfolders = []
    let original_files = []
    const uniqueID = getContext('uniqueID')
    $: locationStatus = window.fs.isDirectory(currentLocation)
    $: parentFolder = locationStatus ? window.path.basename(currentLocation) : 'Undefined'
    const saveLocationToDB = getContext('saveLocationToDB')
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

                if (saveLocationToDB && filetype.length > 2) {
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
        // console.log('File browser mounted')
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

<div class="top__div px-2">
    <i role="presentation" class="material-symbols-outlined" on:click={() => changeDirectory('..')}>arrow_back</i>
    <i
        role="presentation"
        class="material-symbols-outlined animate__animated animate__faster"
        on:animationend={({ target }) => target.classList.remove('animate__rotateIn')}
        on:click={({ target }) => {
            target.classList.add('animate__rotateIn')
            getFilePromise = getfiles(true, true)
        }}>refresh</i
    >
    <CustomIconSwitch bind:toggler={sortFile} icons={['trending_up', 'trending_down']} />
    <div class="ml-auto">
        <span
            role="presentation"
            class="material-symbols-outlined"
            on:click={() => {
                selectAll = !selectAll
                console.log('selected all files')
                selectAll ? (fileChecked = fullfiles.map((file) => (file = file.name))) : (fileChecked = [])
            }}
        >
            {selectAll ? 'remove_done' : 'select_all'}
        </span>
        <i
            role="presentation"
            class="material-symbols-outlined"
            on:click={() => {
                searchSurface.setOpen(true)
            }}>search</i
        >
    </div>
    <MenuSurface
        style="background: var(--background-color);"
        bind:this={searchSurface}
        anchorCorner="TOP_LEFT"
        anchorMargin={{ top: 0, right: 50, bottom: 0, left: 0 }}
    >
        <div class="p-2">
            <Textfield on:keyup={searchfile} bind:value={searchKey} label="Search {filetype} files" />
        </div>
    </MenuSurface>
</div>

<div
    class="main__container"
    id="{uniqueID}-{filetype}_filebrowser"
    style:grid-template-rows={fullfiles.length
        ? otherfolders.length
            ? 'auto 6fr 1fr'
            : 'auto 1fr'
        : otherfolders.length
        ? 'auto auto 1fr'
        : 'auto 1fr'}
>
    <div class="file-dir">
        <i class="material-symbols-outlined">keyboard_arrow_right</i>
        <div class="folder_name__div">
            <div>{parentFolder}</div>
            {#if searchKey}
                <div class="tag is-small is-warning">{searchKey}</div>
                <button
                    class="button tag is-danger"
                    on:click={() => {
                        searchKey = ''
                        searchfile()
                    }}>X</button
                >
            {/if}
        </div>
    </div>

    {#await getFilePromise}
        <div class="mdc-typography--subtitle1 align center">...loading</div>
    {:then _}
        {#if fullfiles.length && mounted}
            <VirtualCheckList
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
            <div style="overflow-y: auto;">
                {#each otherfolders as folder (folder.id)}
                    <div
                        role="presentation"
                        class="align"
                        on:click={() => changeDirectory(folder.name)}
                        transition:slide|local
                    >
                        <i role="presentation" class="material-symbols-outlined">keyboard_arrow_right</i>
                        <div class="mdc-typography--subtitle1" style="cursor: pointer;">{folder.name}</div>
                    </div>
                {/each}
            </div>
        {/if}
    {:catch error}
        <div>{error}</div>
    {/await}
</div>

<style>
    .top__div {
        display: flex;
        align-items: center;
        background-color: #634e96;
        border-radius: 1em;
        margin-bottom: 1em;
    }
    .main__container {
        width: 100%;
        display: grid;
        grid-auto-flow: row;
        overflow-y: hidden;
        gap: 0.1em;
    }
    .file-dir {
        display: grid;
        gap: 0.5em;
        grid-template-columns: auto 1fr;
    }
    .folder_name__div {
        display: grid;
        grid-template-columns: 1fr auto auto;
        gap: 0.1em;
    }
</style>
