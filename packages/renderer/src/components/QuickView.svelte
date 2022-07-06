<script>
    import { browse } from './Layout.svelte'
    import { fade } from 'svelte/transition'

    export let style = ''
    export let title = ''
    export let active = false
    export let footer = true
    export let currentLocation = ''

    async function browse_folder() {
        const [result] = await browse()
        if (!result) return
        currentLocation = result
        window.createToast('Location updated')
    }
</script>

<div class="quickview" class:is-active={active} transition:fade>
    <header class="quickview-header">
        <button class="button is-link" on:click={browse_folder}>Browse</button>
        <div class="subtitle" style="margin:0;">{title}</div>
        <span class="delete is-pulled-right" data-dismiss="quickview" on:click={() => (active = false)} />
    </header>

    <div class="quickview-body">
        <div class="quickview-block" {style}>
            <slot>Contents</slot>
        </div>
    </div>

    {#if footer}
        <footer class="quickview-footer">
            <slot name="footer" />
        </footer>
    {/if}
</div>

<style>
    .quickview-body {
        display: contents;
    }
    .quickview-block {
        display: grid;
        padding: 2em;
        gap: 1em;
        overflow: hidden;
        height: 100%;

        grid-template-rows: auto 1fr;
    }
    .quickview {
        margin: 5em 0;
    }
    footer,
    .quickview {
        background-color: #594098fa;
    }
    .delete {
        background-color: #fafafa;
    }
    .delete:hover {
        background-color: #f14668;
    }
</style>
