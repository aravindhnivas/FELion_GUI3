<script>
    import Modal from '$components/Modal.svelte'
    import FelixPlotWidgets from './FelixPlotWidgets.svelte'
    import { createEventDispatcher } from 'svelte'
    import FelixPlotExtraWidgets from './FelixPlotExtraWidgets.svelte'
    export let active = false
    export let felixPlotWidgets = {}
    export let theoryLocation = ''
    const dispatch = createEventDispatcher()
    let extraWidgetModal = false
    let widgetType = ''
</script>

<!-- {#if active} -->
<Modal bind:active title="FELIX PLOTTING">
    <svelte:fragment slot="content">
        <FelixPlotWidgets bind:felixPlotWidgets {theoryLocation} />
    </svelte:fragment>
    <button
        slot="footerbtn"
        class="button is-link"
        on:click={(e) => {
            dispatch('submit', { event: e })
        }}
    >
        Submit
    </button>
</Modal>
<!-- {/if} -->
<FelixPlotExtraWidgets bind:active={extraWidgetModal} {widgetType} />
