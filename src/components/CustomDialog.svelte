<script>
    import Dialog, {Title, Content, Actions, InitialFocus} from '@smui/dialog';
    import Button, {Label} from '@smui/button';
    import { createEventDispatcher } from 'svelte';

    export let dialog, id="dialog", label1="Yes", label2="Cancel", title, content;
    const dispatch = createEventDispatcher();

    function sendAction(e) { dispatch('response', { action: e.detail.action }); }

</script>
<style>

    * :global(.mdc-dialog__button) {background-color: #5b3ea2;}
    * :global(.mdc-button:not(:disabled)) {background-color: #5b3ea2;}
</style>

<Dialog
  bind:this={dialog}
  aria-labelledby="{id}-title"
  aria-describedby="{id}-content"
  on:MDCDialog:closed={sendAction}
>
  <Title id="{id}-title">{title}</Title>
  <Content id="{id}-content">
    {content}
  </Content>
  <Actions>
    <Button action={label1}>
      <Label>{label1}</Label>
    </Button>
    <Button action={label2} default use={[InitialFocus]}>
      <Label>{label2}</Label>
    </Button>
  </Actions>
</Dialog>

<!-- <Button on:click={() => dialog.open()}><Label>Delete</Label></Button> -->