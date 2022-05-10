<script context="module">
    import { writable } from 'svelte/store'
    const makeStore = (initial = {}) => {
        const { subscribe, set, update } = writable(initial)
        return {
            subscribe,
            set,
            update,
            reset: () => set(initial),
            push(obj) {
                update((n) => {
                    return { ...n, ...obj, open: true }
                })
            },
        }
    }
    export const showConfirm = makeStore({
        open: false,
        title: 'Confirm',
        content: 'Are you sure?',
        callback: null,
    })
</script>

<script>
    import CustomDialog from './CustomDialog.svelte'
    const labels = { label1: 'Yes', label2: 'Cancel' }

    // $: console.log($showConfirm)
    // const closeHandler = (response) => {
    //     // const response = e.detail.response
    //     console.log(response)
    //     $showConfirm.callback?.(response)
    //     showConfirm.reset()
    // }
</script>

<CustomDialog
    bind:open={$showConfirm.open}
    bind:response={$showConfirm.response}
    title={$showConfirm.title}
    content={$showConfirm.content}
    callback={$showConfirm.callback}
    {...labels}
/>
