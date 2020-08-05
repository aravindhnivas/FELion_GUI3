<script>
    
    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';
    export let items=[], fileChecked=[], style="";

</script>

<div {style}>
        <List checklist>
            {#each items as item}
                <Item style="height:2.5em;">
        
                    <Label>{item.name}</Label>
        
                    <Meta><Checkbox bind:group={fileChecked} value={item.name} on:click/></Meta>

                </Item>
                
            {/each}
        </List>
</div>