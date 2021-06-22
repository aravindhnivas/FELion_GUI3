
<script>
  // import {onMount} from "svelte";
  import { createEventDispatcher } from 'svelte';
  export let active =  false, title =  "Title", style="width:60vw", bodyBackground = "#634e96", bodyStyle="max-height: 30em;", contentID="";

  const dispatch = createEventDispatcher()

</script>

<style>
  .modal-card-body {color: black; overflow-y: auto; height: 100%;}
  
  .delete {background-color: #fafafa;}
  .delete:hover {background-color: #f14668;}
  .modal-card-title {margin:0!important;}
  
</style>


<svelte:window on:keydown="{(e)=> {if(e.keyCode===27) active=false}}"/>
<div class="modal" class:is-active={active}>
  <div class="modal-background"></div>
  <div class="modal-card animated fadeIn faster" {style}>


    <header class="modal-card-head">
      <p class="modal-card-title">{title}</p>
      <span class="delete is-pulled-right" on:click="{()=>{active=false; dispatch('closed', {active}) }}"></span>
    </header>

    <section class="modal-card-body" style="background: {bodyBackground}; {bodyStyle}" id="{contentID||window.getID()}"><slot name="content" style="white-space: pre-wrap;"/></section>

    {#if $$slots.footerbtn}

    <footer class="modal-card-foot">
        <div style="margin-left:auto; display:flex;">
          <slot name="footerbtn" /> 

        </div>
      </footer>
    {/if}
    
  </div>
</div>