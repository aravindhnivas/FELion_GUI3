<script context="module">
    import { toast } from '@zerodevx/svelte-toast'
    import CustomDialog from '.../CustomDialog.svelte'
    import AlertBox from '.../AlertBox.svelte'

    export const showConfirm = ({
        title = 'Confirm',
        content = "'Are you sure?'",
        callback = null,
    } = {}) => {
        console.log('showConfirm', { title, content, callback })
        const id = toast.push({
            component: {
                // src: AlertBox,
                src: CustomDialog,
                sendIdTo: 'id',
                props: {
                    open: true,
                    title,
                    content,
                    callback,
                    // callback: (response) => {
                    //     toast.pop(id)
                    //     callback?.(response)
                    // },
                },
            },
            dismissable: false,
            initial: 0,
            theme: {
                '--toastPadding': '0',
                '--toastMsgPadding': '0',
            },
            target: '_confirAlertBox',
        })
    }
</script>

<script>
    // import CustomDialog from './CustomDialog.svelte'
    import { SvelteToast } from '@zerodevx/svelte-toast'
</script>

<div id="confirAlertBox">
    <SvelteToast
        target="_confirAlertBox"
        options={{ initial: 0, intro: { y: 100 } }}
    />
</div>

<style global lang="scss">
    #confirAlertBox {
        ._toastContainer {
            width: 30rem;
            // display: grid;
            // place-content: center;
            // top: 0;
            ._toastItem {
                width: 100%;
                // background: transparent;
                background: #5e469e;
            }
        }
    }
</style>
