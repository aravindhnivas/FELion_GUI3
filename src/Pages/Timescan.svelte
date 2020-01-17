<script>

    import Layout from "../components/Layout.svelte"
    let filetype = "scan"
    let id = "Timescan"
    let scanfiles = [];
    let scan_location = localStorage[`${filetype}_location`] || ""

    $: console.log(`${filetype} updated: ${scan_location}\n${scanfiles}`)
</script>

<Layout {filetype} {id} bind:currentLocation={scan_location} bind:fileChecked={scanfiles}></Layout> 