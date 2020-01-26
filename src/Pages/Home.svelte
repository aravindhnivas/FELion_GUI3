<script>

  import AnimateBox from "../components/AnimateBox.svelte";
  let animation_welcome;
  import {onMount} from "svelte"
  onMount(() => {

    
    animation_welcome = anime
      .timeline({ loop: false })
      .add({
        targets: ".ml5 .line",
        opacity: [0.5, 1],
        scaleX: [0, 1],
        easing: "easeInOutExpo",
        duration: 700, delay:500
      })
      .add({
        targets: ".ml5 .line",
        duration: 600,
        easing: "easeOutExpo",
        translateY: (el, i) => -0.625 + 0.625 * 2 * i + "em"
      })
      .add({
        targets: ".ml5 .letters-left",
        opacity: [0, 1],
        translateX: ["0.5em", 0],
        easing: "easeOutExpo",
        duration: 600,
        offset: "-=300"
      })
      .add({
        targets: ".ml5 .letters-right",
        opacity: [0, 1],
        translateX: ["-0.5em", 0],
        easing: "easeOutExpo",
        duration: 600,
        offset: "-=600"
      })
      .add({
        targets: ".ml5 .letters-subtitle",
        opacity: [0, 1],
        translateX: ["-0.5em", 0],
        easing: "easeOutExpo",
        duration: 600,
        offset: "-=600"
      })
      .add({
        targets: ".ml5",
        opacity: 1,
        duration: 1000,
        easing: "easeOutExpo",
        delay: 1000
      });
  });
</script>

<style>
  #Home {
    margin-top: 15% !important;
    /* display: none; */
  }

  .ml5 {
    position: relative;
    font-weight: 300;
    font-size: 4.5em;
    color: #fafafa;
  }

  .ml5 .text-wrapper {
    position: relative;
    display: inline-block;
    padding-top: 0.1em;
    padding-right: 0.05em;
    padding-bottom: 0.15em;
    line-height: 1em;
  }

  .ml5 .line {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    margin: auto;
    height: 3px;
    width: 100%;
    background-color: #fafafa;
    transform-origin: 0.5 0;
  }
  .ml5 .letters {
    display: inline-block;
    opacity: 0;
  }
  .letters-subtitle {
    font-size: 0.4em;
  }
</style>


<section class="section" id="Home">
  <AnimateBox>

    <h1 class="ml5">
      
      <span class="text-wrapper">
      
        <span class="line line1" />
      
        <span class="letters letters-left">FELion</span>
        <span class="letters letters-right">Spectrum Analyser</span>
        <span class="line line2" />
      
      </span>
      <br />
      
      <span class="letters letters-subtitle"> To analyse FELIX data for FELion Instrument </span>

    </h1>
  
  </AnimateBox>
</section>