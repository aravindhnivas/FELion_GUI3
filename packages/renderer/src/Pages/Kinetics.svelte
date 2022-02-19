<script>
    import ROSAAkinetics from "./timescan/components/ROSAAkinetics.svelte"
    import ROSAA from "./thz/ROSAA.svelte"
    let activeItem = "ROSAAkinetics";
    let kineticMode=false, thzKinetics=false;
    $: if (activeItem) {
        kineticMode = activeItem === "ROSAAkinetics";
        thzKinetics = activeItem === "ROSAA";
    }
</script>

<section id="Kinetics" style="display:block" class="animated fadeIn">

    <div class="main_div">

        <div class="nav box">
            <div class="hvr-glow" class:active={kineticMode} on:click="{()=>activeItem = "ROSAAkinetics"}"> Timescan Kinetics</div>

            <div class="hvr-glow" class:active={thzKinetics} on:click="{()=>activeItem = "ROSAA"}"> THz Kinetics</div>
        </div>

        <div class="content box">
            <div class="subcontent" class:hide={!kineticMode}><ROSAAkinetics/></div>
            <div class="subcontent" class:hide={!thzKinetics}><ROSAA /></div>
        </div>

    </div>

</section>

<style lang="scss">
    #Kinetics {
        padding: 1em;
    }

    .main_div {


        display: grid;
        gap: 1em;
        grid-template-columns: 1fr 10fr;
        .nav {

            display: flex;
            gap: 1em;
            flex-direction: column;
            padding: 0.5em;

            div {
                padding: 0.5em;
                border-radius: 0.5em;

                cursor: pointer;
            }
            .active {box-shadow: 0 0 8px rgb(0 0 0 / 60%);}

        }

        .content .subcontent {
            display: grid;
            overflow: hidden;
            max-height: calc(100vh - 10rem);
            height: calc(100vh - 10rem);
        }
    }

</style>
