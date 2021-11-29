<script>
    
    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';
    import VirtualList from '@sveltejs/svelte-virtual-list';

    export let items=[], fileChecked=[], height="500px", style="", markedFile="";

</script>


<style>

.tag {
        border-radius: 2em;
        margin: 0 1em;
    }



</style>

<div {style}>
    <VirtualList {items} let:item {height}>

        <List checklist>
            <Item style="height:2.5em;">
                <Label >




                    {#if markedFile == item.name}
                        <span class="tag is-warning">b</span>
                    {/if}
                    {item.name}
                </Label>
                <Meta><Checkbox bind:group={fileChecked} value={item.name} on:click/></Meta>
            </Item>
        </List>
    </VirtualList>
</div>