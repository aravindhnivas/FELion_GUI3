<script>

  import Simplewave from "../components/starterpage_animations/Simplewave.svelte";
  import {windowLoaded} from "../js/functions"
</script>

<style>
  #Home {
    padding: 0;
    margin: 0;
  }
</style>


<section class="section animated fadeIn" id="Home">
    {#if $windowLoaded}
    
      {#await window.sleep(500) then value}
        <Simplewave />
      {/await}
    {/if}
</section>