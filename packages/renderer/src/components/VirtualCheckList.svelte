<script>
    import { createEventDispatcher, onMount } from 'svelte'
    import List, { Item, Meta, Label } from '@smui/list'
    import Checkbox from '@smui/checkbox'
    import VirtualList from '@sveltejs/svelte-virtual-list'
    import { difference } from 'lodash-es'

    let className = ''
    export { className as class }
    export let items = []
    // export let height = 'calc(65vh - 4rem)'
    export let markedFile = ''
    export let fileChecked = []
    export let fileSelected = []
    export let ul$style = ''

    const dispatch = createEventDispatcher()
    const dispatch_fileselect_event = (event) => {
        fileChecked = fileSelected
        dispatch('fileselect', { event, fileChecked })
    }

    const fullfileslist = items.map((file) => (file = file.name))
    // $: console.warn({ fileSelected })
    // $: console.info({ fileChecked })
    function selectRange(event, lastfile) {
        if (!(event.shiftKey && fileSelected.length > 0)) return
        // console.log('range select', fullfileslist)
        // console.log(event.shiftKey, event.target)
        const _from = fullfileslist.indexOf(fileSelected.at(-1))
        const _to = fullfileslist.indexOf(lastfile)
        // console.log(_from, _to)
        if (_from < _to) {
            const additionalFiles = fullfileslist.slice(_from, _to + 1)
            fileSelected = [...fileSelected, ...additionalFiles]
        } else {
            const additionalFiles = fullfileslist.slice(_to, _from + 1)
            fileSelected = difference(fileSelected, additionalFiles)
        }
        fileChecked = fileSelected
    }

    onMount(() => {
        dispatch('mount', {})
    })
</script>

<List checklist style="display:contents; padding: 0.5em; {ul$style}" class={className}>
    <VirtualList {items} let:item>
        {@const highlight = markedFile == item.name}
        <Item
            on:click={(e) => {
                selectRange(e, item.name)
            }}
            style="border-radius: 1em; border: {highlight ? 'solid 1px #ffc107' : ''};"
        >
            <Label class={highlight ? 'marked-file' : ''}>{item.name}</Label>
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
