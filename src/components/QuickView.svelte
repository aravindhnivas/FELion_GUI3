<script>
    export let title = "Quick View", active = false, style = "", footer = true;
</script>

<style>

    .quickview {margin: 5em 0;}
    footer, .quickview {background-color: #594098fa;}
    p {color: #fafafa;}
    .delete {background-color: #fafafa;}
    /* .quickview-body {padding: 1em;} */
    .delete:hover {background-color: #f14668;}
    
</style>

<div class="quickview" class:is-active={active}>
  
  <header class="quickview-header">
    <p class="title">{title}</p>
    <span class="delete" data-dismiss="quickview" on:click="{()=>active=false}"></span>
  </header>

  <div class="quickview-body" {style}>
    <div class="quickview-block">
      <slot>Contents</slot>
    </div>
  </div>

  {#if footer}
    <footer class="quickview-footer"> </footer>
  {/if}
</div>