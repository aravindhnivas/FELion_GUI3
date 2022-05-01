<script>
    import Modal from '$components/Modal.svelte'
    import FelixPlotWidgets from './FelixPlotWidgets.svelte'
    import { createEventDispatcher } from 'svelte'
    import FelixPlotExtraWidgets from './FelixPlotExtraWidgets.svelte'
    export let active = false,
        felixPlotWidgets = {},
        theoryLocation
    const dispatch = createEventDispatcher()
    let extraWidgetModal = false,
        widgetType = ''
</script>

{#if active}
    <Modal bind:active title="FELIX PLOTTING">
        <div slot="content" style="height:40vh;">
            <FelixPlotWidgets bind:felixPlotWidgets {theoryLocation} />
        </div>
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
{/if}
<FelixPlotExtraWidgets bind:active={extraWidgetModal} {widgetType} />
