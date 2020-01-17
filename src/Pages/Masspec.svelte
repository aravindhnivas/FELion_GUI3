<script>

    import Layout from "../components/Layout.svelte"
    let filetype = "mass"
    let id = "Masspec"
    let felixfiles = [];
    let felix_location = localStorage[`${filetype}_location`] || ""

    $: console.log(`${filetype} updated: ${felix_location}\n${felixfiles}`)
</script>

<Layout {filetype} {id} bind:currentLocation={felix_location} bind:fileChecked={felixfiles}></Layout> 