<script context="module">
    
    import {writable} from "svelte/store";
    export const filelist = writable([]), filelistBinded = writable([])
    export const bindDialog = writable(0);

</script>

<script>
    import Dialog, {Title, Content} from '@smui/dialog';
    import List, {Item, Meta, Label} from '@smui/list';
    import Checkbox from '@smui/checkbox';

    let title="List", id = "dialogChecklist";

</script>

<style>

    * :global(#dialogChecklist-content .mdc-list-item__text) { color:black }
    * :global(#dialogCheckList-content .mdc-checkbox__native-control:enabled:not(:checked):not(:indeterminate)~.mdc-checkbox__background) {border-color: #6a50ad;}

</style>

<Dialog bind:this={$bindDialog} aria-labelledby="dialogChecklist-title"
    aria-describedby="dialogChecklist-content" class="dialogCheckList">
    <Title id="dialogChecklist-title">{title}</Title>

        <Content id="dialogChecklist-content">
            <List checklist>
                {#each $filelist as file}
                    <Item>
                        <Label>{file}</Label>
                        <Meta> <Checkbox bind:group={$filelistBinded} value={file}/> </Meta>
                    </Item>
                {/each}
            </List>
        </Content>

</Dialog>