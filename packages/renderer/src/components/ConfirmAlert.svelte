<script>
    import { confirmbox } from '$src/svelteWritable'
    import CustomDialog from './CustomDialog.svelte'
    $: console.log($confirmbox)
    const labels = { label1: 'Yes', label2: 'Cancel' }
    const closeHandler = (e) => {
        const response = e.detail.response
        console.warn(`Dialog closed with response`, response)
        $confirmbox.callback?.(response)
        confirmbox.reset()
    }
</script>

<CustomDialog
    bind:open={$confirmbox.open}
    bind:response={$confirmbox.response}
    title={$confirmbox.title}
    content={$confirmbox.content}
    {...labels}
    on:closed={closeHandler}
/>
