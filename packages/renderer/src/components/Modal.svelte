
<script>
  import { createEventDispatcher, onDestroy } from 'svelte'
  export let active = false
  export let title = "Title"
  export let style="width:60vw"
  export let contentID="";
  export let bodyBackground = "#634e96"
  export let headerBackground="#836ac05c"
  export let bodyStyle="max-height: 30em; height: 30em"
  const dispatch = createEventDispatcher()
  onDestroy(()=>active=false)

</script>

<svelte:window on:keydown="{(e)=> {if(e.keyCode===27) active=false}}"/>

<div class="modal" class:is-active={active}>
  <div class="modal-background"></div>

  <div class="modal-card animated fadeIn faster" {style}>

    <header class="modal-card-head" style="background-color: {headerBackground};">
      <p class="modal-card-title">{title}</p>
      <span class="delete is-pulled-right" on:click="{()=>{active=false; dispatch('closed', {active}) }}"></span>
    </header>

    <section class="modal-card-body" 
      style="background: {bodyBackground}; {bodyStyle}" 
      id="{contentID||getID()}">
      <slot name="content" style="white-space: pre-wrap;"/>
    </section>

    {#if $$slots.footerbtn}

    <footer class="modal-card-foot">
        <div style="margin-left:auto; display:flex;">
          <slot name="footerbtn" /> 
        </div>
      </footer>
    {/if}
    
  </div>
</div>


<style>
  .modal-card-body {color: black; overflow-y: auto; height: 100%;}
  .delete {background-color: #fafafa;}
  .delete:hover {background-color: #f14668;}
  .modal-card-title {margin:0!important;}
</style>