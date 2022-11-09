<script lang="ts">
    import QuickView from './QuickView.svelte'
    import FileBrowser from './FileBrowser.svelte'
    import { createEventDispatcher } from 'svelte'

    export let active = false
    export let currentLocation: string
    export let fileChecked: string[]
    export let filetype = ''
    export let title = ''

    const dispatch = createEventDispatcher()
</script>

<QuickView bind:active bind:currentLocation {title}>
    <FileBrowser bind:currentLocation bind:fileChecked {filetype} on:markedFile />
    <div slot="footer" style="margin:auto">
        <button
            class="button is-link"
            on:click={(e) => {
                dispatch('submit', { event: e })
            }}>Submit</button
        >
    </div>
</QuickView>
