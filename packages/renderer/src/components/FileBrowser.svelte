<script>
    import { tick, onMount, afterUpdate, createEventDispatcher } from 'svelte'
    import { slide } from 'svelte/transition'
    import Textfield from '@smui/textfield'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import CustomIconSwitch from '$components/CustomIconSwitch.svelte'
    import VirtualCheckList from '$components/VirtualCheckList.svelte'
    ///////////////////////////////////////////////////////////////////////////

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

    $: locationStatus = fs.existsSync(currentLocation)
    $: parentFolder = locationStatus ? basename(currentLocation) : 'Undefined'

    let searchKey = ''
    const searchfile = () => {
        console.log(searchKey)
        if (!searchKey) {
            fullfiles = original_files
        } else {
            fullfiles = original_files.filter((file) =>
                file.name.includes(searchKey)
            )
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
                const [folderfile, filereadErr] = await fs.readdir(
                    currentLocation
                )
                if (filereadErr) throw filereadErr

                const fileIncludePattern = new RegExp(`.+\\.[^fr]?${filetype}`) // f or r keyword is to avoid getting fscan and rscan files

                original_files = fullfiles = folderfile
                    .filter(
                        (file) =>
                            fileIncludePattern.test(file) &&
                            fs
                                .lstatSync(pathJoin(currentLocation, file))
                                .isFile()
                    )
                    .map((file) => (file = { name: file, id: getID() }))
                    .sort((a, b) => (a.name < b.name ? 1 : -1))

                fullfileslist = fullfiles.map((file) => (file = file.name))
                otherfolders = folderfile
                    .filter((file) =>
                        fs
                            .lstatSync(pathJoin(currentLocation, file))
                            .isDirectory()
                    )
                    .map((file) => (file = { name: file, id: getID() }))
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
                    db.set(`${filetype}_location`, currentLocation)
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
        currentLocation = pathResolve(currentLocation, goto)
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

    async function selectRange(event) {
        await tick()
        if (event.shiftKey && fileChecked.length) {
            const _from = fullfileslist.indexOf(fileChecked.at(0))
            const _to = fullfileslist.indexOf(fileChecked.at(-1))
            if (_from < _to) {
                fileChecked = fullfileslist.slice(_from, _to + 1)
            } else {
                fileChecked = fullfileslist.slice(_to, _from + 1)
            }
        }
    }
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
</script>

<div class="align h-center">
    <i class="material-icons" on:click={() => changeDirectory('..')}
        >arrow_back</i
    >
    <i
        class="material-icons animated faster"
        on:animationend={({ target }) => target.classList.remove('rotateIn')}
        on:click={({ target }) => {
            target.classList.add('rotateIn')
            getFilePromise = getfiles(true, true)
        }}>refresh</i
    >
    <CustomIconSwitch
        bind:toggler={sortFile}
        icons={['trending_up', 'trending_down']}
    />
</div>

<Textfield
    on:keyup={searchfile}
    bind:value={searchKey}
    label="Search {filetype} files"
/>

<CustomSwitch
    bind:selected={selectAll}
    label="Select All"
    on:SMUISwitch:change={() => {
        console.log('Changed')
        selectAll
            ? (fileChecked = fullfiles.map((file) => (file = file.name)))
            : (fileChecked = [])
    }}
/>

<div id="{filetype}_filebrowser" style="width: 100%; overflow-y:auto;">
    <div class="align folderlist">
        <i class="material-icons">keyboard_arrow_right</i>
        <div>{parentFolder}</div>
    </div>

    {#await getFilePromise}
        <div class="mdc-typography--subtitle1 align center">...loading</div>
    {:then value}
        {#if fullfiles.length && mounted}
            <div on:click={selectRange}>
                <VirtualCheckList
                    bind:fileChecked
                    items={fullfiles}
                    {markedFile}
                    on:click={get_marked_file}
                />
            </div>
        {:else if fullfiles.length <= 0}
            <div>No {filetype} here! or try reload files</div>
        {/if}
        <div style="cursor:pointer">
            {#each otherfolders as folder (folder.id)}
                <div
                    class="align"
                    on:click={() => changeDirectory(folder.name)}
                    transition:slide|local
                >
                    <i class="material-icons">keyboard_arrow_right</i>
                    <div class="mdc-typography--subtitle1">{folder.name}</div>
                </div>
            {/each}
        </div>
    {:catch error}
        <div>{error}</div>
    {/await}
</div>
