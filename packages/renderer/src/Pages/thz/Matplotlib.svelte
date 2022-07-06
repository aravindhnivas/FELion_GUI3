<script lang="ts">
    import Modal from '$components/Modal.svelte'
    import VirtualCheckList from '$components/VirtualCheckList.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'
    import { createEventDispatcher, onMount } from 'svelte'
    import ButtonBadge from '$components/ButtonBadge.svelte'

    export let active = false
    export let currentLocation = ''
    let thzfiles = []

    const dispatch = createEventDispatcher()

    $: data_location = window.path.resolve(currentLocation, 'EXPORT')
    // $: fileSelected = thzfiles
    let fileSelected = []
    let items = []
    let loadStatus = { name: 'loading', type: 'warning' }
    const loadfiles = async () => {
        try {
            items = []
            fileSelected = []
            loadStatus = { name: 'loading', type: 'warning' }
            const [files] = await window.fs.readdir(data_location)
            if (!files) {
                loadStatus = { name: 'loaded: empty', type: 'warning' }
                return
            }
            // console.log(files)
            items = files?.filter((file) => file.endsWith('.thz.dat')).map((name) => ({ name, id: window.getID() }))
            loadStatus = { name: 'loaded', type: 'success' }
        } catch (error) {
            loadStatus = { name: 'error', type: 'danger' }
            window.handleError(error)
        }
    }

    onMount(async () => {
        await loadfiles()
    })
    let includeFit = false
</script>

<Modal bind:active title="THz plots">
    <svelte:fragment slot="body_header__div">
        <div class="align">
            <span class="material-icons" on:click={loadfiles}>refresh</span>
            <span class="tag is-{loadStatus.type}">{loadStatus.name}</span>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="body_scrollable__div">
        <VirtualCheckList {items} bind:fileChecked={thzfiles} {fileSelected} height="calc(60vh - 4rem)" />
    </svelte:fragment>

    <svelte:fragment slot="footerbtn">
        <CustomCheckbox bind:value={includeFit} label="includeFit" />
        <ButtonBadge
            on:click={(e) => {
                dispatch('submit', { e, args: { thzfiles, includeFit, location: data_location } })
            }}
        />
    </svelte:fragment>
</Modal>
