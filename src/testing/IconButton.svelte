<script>

    import IconButton, {Icon} from '@smui/icon-button';
    let starred = false;
    function doSomething() {
        alert('something');
    }

    $: console.log(starred)
    
</script>

<IconButton class="material-icons" on:click={doSomething}>build</IconButton>

<IconButton toggle bind:pressed={starred}>
  <Icon class="material-icons" on>star</Icon>
  <Icon class="material-icons">star_border</Icon>
</IconButton>