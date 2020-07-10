<script>
    export let active =  false, title =  "Title", style="width:60vw";
    let content;

</script>

<style>

  .modal-card-body {color: black; overflow-y: auto; max-height: 30em; background: #634e96;}
  /* .modal-card {width: 60vw;} */
  .delete {background-color: #fafafa;}
  .delete:hover {background-color: #f14668;}

</style>

<div class="modal" class:is-active={active}>

  <div class="modal-background"></div>

  <div class="modal-card animated fadeIn faster" {style}>

    <header class="modal-card-head">
      <p class="modal-card-title">{title}</p>
      <span class="delete is-pulled-right" on:click="{()=>active=false}"></span>
    </header>

    <section class="modal-card-body"><slot name="content" {content}/></section>

    <footer class="modal-card-foot">
      <div style="margin-left:auto; display:flex;">
        <slot name="footerbtn" /> 
        <!-- <button class="button is-link" on:click={()=>active = false}>Cancel</button> -->
    
      </div>
    </footer>

  </div>

</div>