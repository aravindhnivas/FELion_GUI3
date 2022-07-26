<script>
    import IconButton, { Icon } from '@smui/icon-button'
    export let toggler = false
    export let style = ''
    export let icons = []
</script>

<IconButton {style} toggle bind:pressed={toggler} on:click>
    <Icon class="material-symbols-outlined" on>{icons[0]}</Icon>
    <Icon class="material-symbols-outlined">{icons[1]}</Icon>
</IconButton>
