
<script>
  
  import { Snackbar } from 'svelma';
  import { Modal } from './Modal.svelte';
  
  export let preModal = {}

  let active=false;

  function openModal() {
    Snackbar.create({ 

      message: preModal.message, position:"is-top", type:`is-${preModal.type}`, duration: 5000,

      actionText: preModal.actionText, onAction: ()=>{ active = true; }
    
    })
    
    preModal.open = false;
  }

  $: if(preModal.open) openModal()

</script>

<Modal bind:active title={preModal.modalTitle}>

  <div slot="content">{preModal.modalContent}</div>
</Modal>