<script>
    import { toast } from '@zerodevx/svelte-toast'
    export let id = ''
    export let title = ''
    // export let open = false
    export let content = ''
    export let labels = ['Yes', 'Cancel']
    // export let label2 = 'Cancel'
    export let response = 'Yes'
    export let callback = null
    const choosenOption = (label) => {
        response = label
        callback?.(response)

        // dispatch('closed', { event, response: action })
        // open = false
        toast.pop(id)
    }
</script>

<!-- {#if open} -->
<div class="mdc-dialog__scrim" />
<div class="alert elevated" {id}>
    <h2 class="subtitle">{title}</h2>
    <div class="">{content}</div>
    <div class="footer">
        <button class="button is-link" on:click={() => choosenOption(labels[0])}
            >{labels[0]}</button
        >
        <button
            class="button is-danger"
            on:click={() => choosenOption(labels[1])}>{labels[1]}</button
        >
    </div>
</div>

<!-- {/if} -->
<style lang="scss">
    .alert {
        // * {
        //     color: black;
        // }
        background: #5e469e;
        min-width: 30vw;
        padding: 1em;
        flex-direction: column;
    }
    .footer,
    .alert {
        display: flex;
        gap: 1em;
    }
    .footer {
        margin-left: auto;
    }
</style>
