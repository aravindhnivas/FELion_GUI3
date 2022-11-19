<script lang="ts">
    import { createEventDispatcher } from 'svelte'
    import { felixPeakTable } from '../functions/svelteWritables'
    import Modal from '$components/Modal.svelte'
    import STable from '$components/STable.svelte'

    export let active = false

    const dispatch = createEventDispatcher()
    console.log('felixPeakTable', felixPeakTable)
    const uniqueID = getContext<string>('uniqueID')
</script>

{#if active}
    <Modal bind:active title="Adjust initial guess">
        <svelte:fragment slot="content">
            <STable
                maxHeight="100%"
                headKeys={['Frequency', 'Intensity', 'Sigma']}
                rowKeys={['freq', 'amp', 'sig']}
                bind:rows={$felixPeakTable[uniqueID]}
                closeableRows={true}
                editable={true}
                sortable={true}
            />
        </svelte:fragment>
        <button slot="footerbtn" class="button is-link" on:click={() => dispatch('save')}>Save</button>
    </Modal>
{/if}
