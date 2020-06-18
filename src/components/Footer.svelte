<script>
  import {onMount, afterUpdate} from "svelte";
  import {windowLoaded} from "../js/functions";
  import {activePage} from "./Navbar.svelte";
  
  afterUpdate(()=>{
    $activePage === "Home" ? hidepage("footer") : showpage("footer")

  })
  
</script>
<style>

    .navbar { background: #38236b; }

</style>

<nav class="navbar is-fixed-bottom animated fadeInUp" id="footer" style="display:none">
  <div class="navbar-menu">
    <div class="navbar-start">

      <div class="navbar-item">
        <p>Developed at Dr.Br&uuml;nken's group FELion@FELIX</p>
      </div>
    </div>

    <div class="navbar-end">
      <div class="navbar-item">

        <p>2020 &copy; AN Marimuthu | MIT License<p>
      </div>
    </div>
  </div>
</nav>