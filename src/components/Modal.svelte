
<script>
  
  import { Snackbar } from 'svelma'
  export let modalTitle, modalContent, activated = false, type="danger", msg="Error Occured", actionText="Show in detail";
  let active=false;
  function openModal(err) {

    Snackbar.create({ 
        message: msg, position:"is-top", type:`is-${type}`, 
        actionText: actionText, onAction: ()=>{ active = true; }
    })

  }

  $: if (activated) openModal()

</script>

<div class="modal" class:is-active={active}>
  <div class="modal-background"></div>
  <div class="modal-card">
    <header class="modal-card-head">
      <p class="modal-card-title">{modalTitle}</p>
    </header>
    <section class="modal-card-body"> {modalContent} </section>

    <footer class="modal-card-foot">
      <button class="button is-link" on:click={()=>activated = active = false}>Cancel</button>
    </footer>

  </div>
</div>