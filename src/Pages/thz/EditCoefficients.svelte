
<script>
    // import { createEventDispatcher } from 'svelte';
    import Modal from '../../components/Modal.svelte';
    import Table from "../../components/Table.svelte"
    export let active=false, coefficients = [], title="Title";
    // const dispatch = createEventDispatcher();

</script>

{#if active}
    <Modal bind:active {title} >

        <div slot="content" >

            <Table head={["Label", "Value"]} keys={["label", "value"]} bind:rows={coefficients} sortOption={false}/>

        </div>


        <button slot="footerbtn" class="button is-link" on:click="{()=>active=false}" >Close</button>
    </Modal>
{/if}