<script>

    import Layout from "../components/Layout.svelte"
    let filetype = "mass"
    let id = "Masspec"
    let massfiles = [];
    let mass_location = localStorage[`${filetype}_location`] || ""

    $: console.log(`${filetype} updated: ${mass_location}\n${massfiles}`)
</script>

<Layout {filetype} {id} bind:currentLocation={mass_location} bind:fileChecked={massfiles}></Layout> 