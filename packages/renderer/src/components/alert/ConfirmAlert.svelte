<script>
    import { showConfirm } from './store'
    import Dialog from './Dialog.svelte'
</script>

<Dialog
    bind:open={$showConfirm.open}
    title={$showConfirm.title}
    content={$showConfirm.content}
    callback={$showConfirm.callback}
/>
