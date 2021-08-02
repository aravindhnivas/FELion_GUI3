
<script>
    import Modal from './Modal.svelte'
    import Table from "./Table.svelte"
    
    export let active=false, title="Title", rows = [], keys = [], userSelect=true;
    export let sortOption = false, closeOption = true, addextraOption = true, animateRow = false;

</script>

{#if active}
    <Modal bind:active {title} >
    
        <svelte:fragment slot="content">
            <Table head={keys} {keys} bind:rows {sortOption} {closeOption} {addextraOption} {animateRow} {userSelect}/>
        </svelte:fragment>
        <svelte:fragment slot="footerbtn">
            <slot name="footer"><button class="button is-link" on:click="{()=>active=false}" >Close</button></slot>


        </svelte:fragment>
    </Modal>
{/if}