<script>
    import { createEventDispatcher } from 'svelte'
    import Dialog, { Title, Content, Actions, InitialFocus } from '@smui/dialog'
    import Button, { Label } from '@smui/button'
    export let id = window.getID()
    export let title = ''
    export let open = false
    export let content = ''
    export let label1 = 'Yes'
    export let label2 = 'Cancel'
    export let response = 'Yes'
    export let callback = null

    const dispatch = createEventDispatcher()

    const closeHandler = (event) => {
        const response = event.detail.action
        callback?.(response)
        dispatch('response', { event, response })
    }
</script>

<Dialog
    bind:open
    aria-labelledby="{id}-title"
    aria-describedby="{id}-content"
    scrimClickAction=""
    escapeKeyAction=""
    on:SMUIDialog:closed={closeHandler}
>
    <Title id="{id}-title">{title}</Title>
    <Content id="{id}-content">{content}</Content>
    <Actions>
        <Button action={label1} on:click={() => (response = label1)}>
            <Label>{label1}</Label>
        </Button>
        <Button
            action={label2}
            default
            use={[InitialFocus]}
            on:click={() => (response = label2)}
        >
            <Label>{label2}</Label>
        </Button>
    </Actions>
</Dialog>
