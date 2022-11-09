<script lang="ts">
    import Modal from '$components/Modal.svelte'
    import FelixPlotWidgets from './FelixPlotWidgets.svelte'
    import { createEventDispatcher } from 'svelte'
    // import FelixPlotExtraWidgets from './FelixPlotExtraWidgets.svelte'

    export let active = false
    export let felixPlotWidgets: {
        text: ValueLabel<string>[]
        boolean: ValueLabel<boolean>[]
        number: ValueLabel<string>[]
    }

    const dispatch = createEventDispatcher()
    // let extraWidgetModal = false
    // let widgetType = ''
</script>

<Modal bind:active title="FELIX PLOTTING">
    <svelte:fragment slot="content">
        <FelixPlotWidgets bind:felixPlotWidgets />
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
<!-- <FelixPlotExtraWidgets bind:active={extraWidgetModal} {widgetType} /> -->
