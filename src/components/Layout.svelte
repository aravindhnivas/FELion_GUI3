<script>
    
    import LoremIpsum from "../testing/LoremIpsum.svelte"
    export let id;

</script>

<style lang="scss">

    .filebrowser, .fileContainer {
        background-image: url(./assets/css/intro.svg);
        max-height: calc(100vh - 8.8em);
        overflow-y: auto;
        padding-left: 2em;
    }
    .container {padding: 5em;}
    
</style>

<section {id} style="display:none">

    <div class="columns">

        <div class="column is-2 box filebrowser">
            <h1>{id}</h1>
            <hr>
            <LoremIpsum n={100} />
        </div>


        <div class="column fileContainer">
            <div class="container box">
                <h1>{id}</h1>
                <hr>
                <LoremIpsum n={100} />
            </div>
        </div>

    </div>
</section>