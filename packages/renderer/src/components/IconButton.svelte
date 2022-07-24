<script lang="ts">
    import IconButton, { Icon } from '@smui/icon-button'
    export let value = false
    export let icons: { on: string; off: string } = { on: '', off: '' }
    export let style = ''
</script>

<IconButton toggle bind:pressed={value} {style}>
    <Icon class="material-icons" on>{icons.on}</Icon>
    <Icon class="material-icons">{icons.off}</Icon>
</IconButton>
