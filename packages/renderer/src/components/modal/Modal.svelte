<script>
    import Dialog, { Title, Content, Actions } from '@smui/dialog'
    import { createEventDispatcher, onMount } from 'svelte'

    export let id = getID()
    export let active = false
    export let title = ''
    let className = ''
    export { className as class }
    export let content$style = ''

    const dispatch = createEventDispatcher()

    onMount(() => {
        dispatch('mounted')
        return () => dispatch('destroyed')
    })
</script>

<Dialog
    bind:open={active}
    scrimClickAction=""
    surface$class="background-body {className}"
    aria-labelledby="{id}-title"
    aria-describedby="{id}-content"
    surface$style="min-width: 30vw; min-height: 30vh;  max-width:60vw; max-height: 70vh; background-color: #5a419b;"
    on:SMUIDialog:closed={(e) => dispatch('closed', { event: e })}
>
    <Title style="color: white; background: #836ac05c;" id="{id}-title"
        >{title}</Title
    >
    <Content id="{id}-content" style={content$style}>
        <slot name="content" />
    </Content>
    <Actions style="background: #836ac05c;">
        <div class="action-btns">
            <slot name="footer" />
            <button class="button is-danger" on:click={() => (active = false)}
                >Close</button
            >
        </div>
    </Actions>
</Dialog>

<style>
    .action-btns {
        display: flex;
        gap: 1em;
    }
</style>
