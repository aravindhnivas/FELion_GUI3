<script>
    import Simplewave from '$components/starterpage_animations/Simplewave.svelte'
    import { windowLoaded } from '../js/functions'
</script>

<section
    class="section animate__animated animate__fadeIn"
    id="Home"
    style="display:none"
>
    {#if $windowLoaded}
        {#await window.sleep(500) then _}
            <Simplewave>
                <svelte:fragment slot="header">
                    <h1 class="title">FELion Spectrum Analyser</h1>
                    <h1 class="subtitle">
                        To analyse FELIX data for FELion Instrument
                    </h1>
                </svelte:fragment>

                <svelte:fragment slot="footer">
                    <p>
                        Developed at Dr.Br&uuml;nken's group FELion@FELIX | 2021
                        &copy; AN Marimuthu
                    </p>
                </svelte:fragment>
            </Simplewave>
        {/await}
    {/if}
</section>

<style>
    #Home {
        padding: 0;
        margin: 0;
        height: 100%;
    }

    h1 {
        letter-spacing: 2px;
    }

    .title {
        font-size: 4em;
    }

    p {
        color: black;
    }

    @media (max-width: 768px) {
        .title {
            font-size: 3em;
        }
    }
</style>
