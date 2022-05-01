<script>
    import Modal from './Modal.svelte'
    import Table from './Table.svelte'

    export let rows = []
    export let keys = []
    export let title = ''
    export let active = false
    export let userSelect = true
    export let animateRow = false
    export let sortOption = false

    export let closeOption = true
    export let addextraOption = true
</script>

{#if active}
    <Modal bind:active {title}>
        <svelte:fragment slot="content">
            <Table
                head={keys}
                {keys}
                bind:rows
                {sortOption}
                {closeOption}
                {addextraOption}
                {animateRow}
                {userSelect}
            >
                <svelte:fragment slot="header">
                    <slot name="header" />
                </svelte:fragment>
            </Table>
        </svelte:fragment>
        <svelte:fragment slot="footerbtn">
            <slot name="footer"
                ><button
                    class="button is-link"
                    on:click={() => (active = false)}>Close</button
                ></slot
            >
        </svelte:fragment>
    </Modal>
{/if}
