
<script>
  import {mainPreModal} from "../svelteWritable";
  import { Snackbar } from 'svelma';
  import Modal from './Modal.svelte';
  
  // export let $mainPreModal = {}

  let active=false;

  function openModal() {
    Snackbar.create({ 

      message: $mainPreModal.message || "Error Occured", position:"is-top", type:`is-${$mainPreModal.type || "danger"}`, duration: 5000,

      actionText: $mainPreModal.actionText || "Show Details", onAction: ()=>{ active = true; }
    
    })

    
    $mainPreModal.open = false;
    
  }

  $: if($mainPreModal.open) {openModal()}

  $: console.log($mainPreModal)
  let headerBackground="#836ac05c";
  $: if(active) {headerBackground = $mainPreModal.type === "danger" ? "#f14668" : "#836ac05c" }
</script>

{#if active}
  <Modal bind:active title={$mainPreModal.modalTitle || "Error details"} bodyBackground="#634e96" {headerBackground} >
    <div slot="content" style="color:#fafafa; white-space: pre-wrap; user-select:text;">{$mainPreModal.modalContent}</div>
  </Modal>
{/if}