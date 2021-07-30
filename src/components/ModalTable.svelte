
<script>
    import Modal from './Modal.svelte'
    import Table from "./Table.svelte"
    
    export let active=false, title="Title", rows = [], keys = [];
</script>

{#if active}
    <Modal bind:active {title} >
        <svelte:fragment slot="content">
            <Table head={keys} {keys} bind:rows sortOption={false}/>

        </svelte:fragment>
        <svelte:fragment slot="footerbtn">
            <slot name="footer"><button class="button is-link" on:click="{()=>active=false}" >Close</button></slot>
        </svelte:fragment>
    </Modal>

    {/if}