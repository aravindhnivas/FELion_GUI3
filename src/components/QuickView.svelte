<script>
  import {browse} from "./Layout.svelte";
  import { fade } from 'svelte/transition';

  export let active = false, style = "", footer = true, currentLocation="", title="";
  
  function browse_folder() {
  
    browse({dir:true}).then(result=>{
        if (result) { currentLocation = result[0]; window.createToast("Location updated") }
    })
  }

</script>

<style>
    .quickview {margin: 5em 0;}

    footer, .quickview {background-color: #594098fa;}
    /* p {color: #fafafa;} */
    .delete {background-color: #fafafa;}
    .delete:hover {background-color: #f14668;}
</style>

<div class="quickview" class:is-active={active} transition:fade>

  <header class="quickview-header">

    <button class="button is-link" on:click={browse_folder}>Browse</button>
    <div class="subtitle" style="margin:0;">{title}</div>
    <span class="delete is-pulled-right" data-dismiss="quickview" on:click="{()=>active=false}"></span>

  </header>

  <div class="quickview-body" {style}>
    <div class="quickview-block">
      <slot >Contents</slot>
    </div>
  </div>

  {#if footer}
    <footer class="quickview-footer">
      <slot name="footer" />
    </footer>
  {/if}
</div>