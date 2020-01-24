<script>
    
    import IconButton, {Icon} from '@smui/icon-button'
    
    export let icons = [], toggler="", style=""

</script>

<IconButton {style} toggle bind:pressed={toggler} on:click>
    <Icon class="material-icons" on>{icons[0]}</Icon>
    <Icon class="material-icons">{icons[1]}</Icon>
</IconButton>