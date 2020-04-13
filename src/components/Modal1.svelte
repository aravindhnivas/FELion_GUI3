<script>
    export let active =  false, title =  "Title"
    let content;
</script>

<style>
.modal-card-body {color: black; overflow-y: auto; max-height: 30em; background: #634e96;}
.modal-card {width: 60vw;}

</style>

<div class="modal" class:is-active={active}>
  <div class="modal-background"></div>

  <div class="modal-card">
    <header class="modal-card-head">
      <p class="modal-card-title">{title}</p>

    </header>

    <section class="modal-card-body"><slot name="content" {content}/>  </section>
    <footer class="modal-card-foot">
      <div style="margin-left:auto; display:flex;">
        <slot name="footerbtn" /> 
        <button class="button is-link" on:click={()=>active = false}>Cancel</button>
      </div>
    </footer>

  </div>

</div>