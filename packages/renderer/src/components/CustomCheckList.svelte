<script>
    import List, { Item, Meta, Label } from '@smui/list'
    import Checkbox from '@smui/checkbox'

    export let style = ''
    export let item$style = ''
    export let items = []
    export let fileChecked = []

    let className = ''
    export { className as class }
</script>

<div class={className} {style}>
    <List checklist>
        {#each items as item (item.name)}
            <Item style="height:2.5em; {item$style}">
                <Label>{item.name}</Label>
                <Meta><Checkbox bind:group={fileChecked} value={item.name} on:click /></Meta>
            </Item>
        {/each}
    </List>
</div>
