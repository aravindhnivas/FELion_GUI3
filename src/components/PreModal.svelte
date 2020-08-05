
<script>
  
  import { Snackbar } from 'svelma';
  import Modal from './Modal.svelte';
  
  export let preModal = {}

  let active=false;

  function openModal() {
    Snackbar.create({ 

      message: preModal.message || "Error Occured", position:"is-top", type:`is-${preModal.type || "danger"}`, duration: 5000,

      actionText: preModal.actionText || "Show Details", onAction: ()=>{ active = true; }
    
    })
    
    preModal.open = false;
  }

  $: if(preModal.open) openModal()

</script>

<Modal bind:active title={preModal.modalTitle || "Error details"} bodyBackground="#fafafa">

  <div slot="content" style="color:black; white-space: pre; user-select:text;">{preModal.modalContent}</div>
</Modal>