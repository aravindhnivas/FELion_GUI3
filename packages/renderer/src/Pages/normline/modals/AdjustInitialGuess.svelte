<script>
    import { createEventDispatcher } from 'svelte'
    import { felixPeakTable } from '../functions/svelteWritables'
    import Modal from '$components/Modal.svelte'
    import Table from '$components/Table.svelte'

    export let active = false
    const dispatch = createEventDispatcher()
    $: console.log(`peakTable:`, $felixPeakTable)
</script>

{#if active}
    <Modal bind:active title="Adjust initial guess">
        <svelte:fragment slot="content">
            <Table
                head={['Frequency', 'Amplitude', 'Sigma']}
                keys={['freq', 'amp', 'sig']}
                bind:rows={$felixPeakTable}
                sortOption={true}
            />
        </svelte:fragment>
        <button slot="footerbtn" class="button is-link" on:click={() => dispatch('save')}>Save</button>
    </Modal>
{/if}
