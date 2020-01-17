<script>

    import Layout from "../components/Layout.svelte"
    let filetype = "felix"
    let id = "Normline"
    let felixfiles = [];
    let location = localStorage[`${filetype}_location`] || ""

    $: console.log("Normline update: ", location)
</script>

<Layout {filetype} {id} bind:currentLocation={location} bind:fileChecked={felixfiles}></Layout> 