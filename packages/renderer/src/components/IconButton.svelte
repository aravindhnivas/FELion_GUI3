<script>
    export let value = false
    export let label = ''
    export let icons = []
    export let style = ''
</script>

<button {style} class="button is-link" on:click={() => (value = !value)}>
    {label}
    <i class=" material-icons">{value ? icons[0] : icons[1]}</i>
</button>
