
<script>
    export let active =  false, title =  "Title", style="width:60vw", bodyBackground = "#634e96";
</script>

<style>
  .modal-card-body {color: black; overflow-y: auto; max-height: 30em;}
  .delete {background-color: #fafafa;}
  
  .delete:hover {background-color: #f14668;}
</style>

<svelte:window on:keydown="{(e)=> {if(e.keyCode===27) active=false}}"/>

<div class="modal" class:is-active={active}>

  <div class="modal-background"></div>

  <div class="modal-card animated fadeIn faster" {style}>

    <header class="modal-card-head">
      <p class="modal-card-title">{title}</p>
      <span class="delete is-pulled-right" on:click="{()=>active=false}"></span>
    </header>

    <section class="modal-card-body" style="background: {bodyBackground};"><slot name="content" style="white-space: pre;"/></section>

    <footer class="modal-card-foot">
      <div style="margin-left:auto; display:flex;">
        <slot name="footerbtn" /> 
      </div>
    </footer>
  </div>

</div>