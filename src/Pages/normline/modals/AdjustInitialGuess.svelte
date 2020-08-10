
<script>
    import {felixPeakTable} from '../functions/svelteWritables';
    // import Ripple from '@smui/ripple';
    import { fade } from 'svelte/transition'
    import { createEventDispatcher } from 'svelte';
    import Modal from '../../../components/Modal.svelte';

    import {Icon} from '@smui/icon-button';

    import Table from "../../../components/Table.svelte"
    
    export let active=false;
    const dispatch = createEventDispatcher();

    $: console.log(`peakTable:`, $felixPeakTable)

</script>

<style>

</style>

{#if active}

    <Modal bind:active title="Adjust initial guess" >
        <div slot="content" >
            <Table head={["Frequency", "Amplitude", "Sigma"]} keys={["freq", "amp", "sig"]} bind:rows={$felixPeakTable} sortOption={true}/>

        </div>

        <button slot="footerbtn" class="button is-link" on:click="{()=>dispatch('save')}" >Save</button>
    </Modal>
{/if}