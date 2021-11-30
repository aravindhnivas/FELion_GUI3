
<script>
    import QuickView from "./QuickView.svelte"
    import FileBrowser from "./FileBrowser.svelte"
    import { createEventDispatcher } from 'svelte';

    export let active=false, currentLocation, fileChecked, filetype="", title="";

    const dispatch = createEventDispatcher();
</script>

<svelte:window on:keydown="{(e)=> {if(e.keyCode===27) active=false}}"/>

<QuickView style="padding:1em; display: grid; justify-items: center;" bind:active bind:currentLocation {title}>
    <FileBrowser bind:currentLocation bind:fileChecked {filetype} on:markedFile />
    <div slot="footer" style="margin:auto">
        <button class="button is-link" on:click="{(e)=>{dispatch('submit', { event:e })}}">Submit</button>
    </div>
</QuickView>