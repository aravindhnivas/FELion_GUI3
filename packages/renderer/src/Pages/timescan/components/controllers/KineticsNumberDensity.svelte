<script>
    import Modal from '$components/modal/Modal.svelte'
    import NumberDensity from '$src/Pages/misc/NumberDensity.svelte'

    export let nHe = ''

    export let open = false
    export let args = {}
    export let currentConfig = {}

    $: console.log('number density: ', args)
</script>

<Modal bind:open title="Number density: {nHe} cm-3" id="kinetis-number-density">
    <svelte:fragment slot="content">
        <NumberDensity
            {currentConfig}
            bind:args
            on:getValue={(e) => {
                nHe = e.detail.nHe
            }}
        />
    </svelte:fragment>
</Modal>
