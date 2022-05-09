<script>
    import { createEventDispatcher } from 'svelte'
    import List, { Item, Meta, Label } from '@smui/list'
    import Checkbox from '@smui/checkbox'
    import VirtualList from '@sveltejs/svelte-virtual-list'
    export let style = ''
    export let items = []
    export let height = '600px'
    export let markedFile = ''
    export let fileChecked = []
    export let fileSelected = []
    $: console.warn({ fileChecked })

    const dispatch = createEventDispatcher()
    const dispatch_fileselect_event = (event) => {
        fileChecked = fileSelected
        dispatch('fileselect', { event, fileChecked })
        // console.log('fileselect event dispatched')
    }
</script>

<div {style}>
    <List checklist>
        <VirtualList {items} let:item {height}>
            {@const highlight = markedFile == item.name}
            <Item
                style="border-radius: 1em; border: {highlight
                    ? 'solid 1px #ffc107'
                    : ''};"
            >
                <Label class={highlight ? 'marked-file' : ''}>{item.name}</Label
                >
                <Meta
                    ><Checkbox
                        bind:group={fileSelected}
                        value={item.name}
                        on:click
                        on:change={dispatch_fileselect_event}
                    /></Meta
                >
            </Item>
        </VirtualList>
    </List>
</div>

<style global>
    .mdc-deprecated-list {
        padding-right: 1em;
    }
</style>
