<script>
    
    import IconButton, {Icon} from '@smui/icon-button'
    
    export let icons = [], toggler=""

</script>

<IconButton toggle bind:pressed={toggler}>
    <Icon class="material-icons" on>{icons[0]}</Icon>
    <Icon class="material-icons">{icons[1]}</Icon>
</IconButton>