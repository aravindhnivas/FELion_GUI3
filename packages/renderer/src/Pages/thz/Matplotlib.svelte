<script lang="ts">
    import Modal from '$components/Modal.svelte'
    import VirtualCheckList from '$components/VirtualCheckList.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'
    import { createEventDispatcher, onMount } from 'svelte'
    import ButtonBadge from '$components/ButtonBadge.svelte'

    export let active = false
    export let currentLocation = ''
    let thzfiles: string[] = []

    const dispatch = createEventDispatcher()

    $: data_location = window.path.resolve(currentLocation, 'EXPORT')
    $: if (data_location) {
        thzfiles = []
        loadfiles()
    }

    let fileSelected: string[] = []
    let items: { name: string; id: string }[] = []
    let loadStatus = { name: 'loading', type: 'warning' }

    const loadfiles = async () => {
        items = []
        fileSelected = []
        thzfiles = []
        loadStatus = { name: 'loading', type: 'warning' }
        const files = await window.fs.readdir(data_location)
        if (window.fs.isError(files)) {
            loadStatus = { name: 'error', type: 'danger' }
            return
        }
        items = files?.filter((file) => file.endsWith('.thz.dat')).map((name) => ({ name, id: window.getID() }))
        loadStatus = { name: 'loaded', type: 'success' }
    }

    onMount(async () => {
        await loadfiles()
    })
    let includeFit = false
</script>

<Modal bind:active title="THz plots">
    <svelte:fragment slot="body_header__div">
        <div class="align">
            <span role="presentation" class="material-symbols-outlined" on:click={loadfiles}>refresh</span>
            <span class="tag is-{loadStatus.type}">{loadStatus.name}</span>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="body_scrollable__div">
        <VirtualCheckList {items} bind:fileChecked={thzfiles} {fileSelected} ul$style={'overflow-y: auto;'} />
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
