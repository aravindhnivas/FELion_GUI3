<script context="module">
  import {writable} from "svelte/store";
  export const activated =  writable(false), modalContent =  writable("")
  export const modalTitle =  writable("Error detail"), modalType =  writable("danger"), modalPreMsg = writable("Error Occured")

</script>

<script>
  
  import { Snackbar } from 'svelma'
  let actionText="Show details";
  let active=false;

  function openModal(err) {

    Snackbar.create({ 

      message: $modalPreMsg, position:"is-top", type:`is-${$modalType}`, duration: 5000,
      actionText: actionText, onAction: ()=>{ active = true; }
    })
    $activated = false;
  }

  $: if($activated) openModal()
</script>

<style>

.modal-card-body {color: black; overflow-y: auto}
.modal-card {width: 60vw;}
</style>

<div class="modal" class:is-active={active}>

  <div class="modal-background"></div>
  <div class="modal-card">
    <header class="modal-card-head">
      <p class="modal-card-title">{$modalTitle}</p>
    </header>

    <section class="modal-card-body"> {$modalContent} </section>

    <footer class="modal-card-foot">
      <button class="button is-link" style="margin-left:auto;" on:click={()=>active = false}>Cancel</button>
    </footer>

  </div>
</div>