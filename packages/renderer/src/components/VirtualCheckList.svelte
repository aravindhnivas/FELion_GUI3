<script>
    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';
    import VirtualList from '@sveltejs/svelte-virtual-list';
    
    export let style=""
    export let items=[]
    export let height="600px"
    export let markedFile="";
    export let fileChecked=[]

</script>

<div {style} >

    <VirtualList {items} let:item {height}>
        {@const highlight = markedFile == item.name}
        <List checklist>
            <Item
                style="border-radius: 1em; border: {highlight ? 'solid 1px #ffc107': ''}" >
                <Label>{item.name}</Label>
                <Meta><Checkbox bind:group={fileChecked} value={item.name} on:click/></Meta>
            </Item>
        </List>
    </VirtualList>

</div>
