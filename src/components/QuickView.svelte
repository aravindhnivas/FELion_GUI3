<script>
  export let active = false, style = "", footer = true, location=""
  import {browse, createToast} from "./Layout.svelte"
  function browse_folder() {
    browse({dir:true}).then(result=>{
        if (!result.canceled) {
          location = result.filePaths[0]; createToast("Location updated")

        }
    })
  }

</script>

<style>
    .quickview {margin: 5em 0;}

    footer, .quickview {background-color: #594098fa;}
    p {color: #fafafa;}
    .delete {background-color: #fafafa;}
    .delete:hover {background-color: #f14668;}
</style>

<div class="quickview" class:is-active={active}>
  <header class="quickview-header">
    <button class="button is-link" on:click={browse_folder}>Browse</button>
    <span class="delete is-pulled-right" data-dismiss="quickview" on:click="{()=>active=false}"></span>

  </header>

  <div class="quickview-body" {style}>
    <div class="quickview-block">
      <slot>Contents</slot>
    </div>
  </div>

  {#if footer}
    <footer class="quickview-footer">
      <slot name="footer" />
    </footer>
  {/if}
</div>