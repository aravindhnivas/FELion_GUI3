<script>

    import Layout from "../components/Layout.svelte"
    let filetype = "thz"
    let id = "THz"
    let thzfiles = [];
    let thz_location = localStorage[`${filetype}_location`] || ""

    $: console.log(`${filetype} updated: ${thz_location}\n${thzfiles}`)
</script>

<Layout {filetype} {id} bind:currentLocation={thz_location} bind:fileChecked={thzfiles}></Layout> 