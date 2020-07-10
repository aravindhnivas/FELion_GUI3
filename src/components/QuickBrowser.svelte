
<script>
    import QuickView from "./QuickView.svelte"
    import FileBrowser from "./FileBrowser.svelte"
    import { createEventDispatcher } from 'svelte';

    export let active, currentLocation, fileChecked, filetype="";

    const dispatch = createEventDispatcher();
</script>

{#if active}

    <QuickView style="padding:1em;" bind:active bind:currentLocation>

        <FileBrowser bind:currentLocation bind:fileChecked {filetype}/>
        <div slot="footer" style="margin:auto">
            <button class="button is-link" on:click="{(e)=>{dispatch('submit', { event:e })}}">Submit</button>

        </div>

    </QuickView>
{/if}