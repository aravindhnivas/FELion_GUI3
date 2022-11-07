<script lang="ts">
    import IconButton, { Icon } from '@smui/icon-button'
    import { afterUpdate, createEventDispatcher, tick } from 'svelte'
    export let value = false
    export let icons: { on: string; off: string } = { on: '', off: '' }
    export let style = ''
    const dispatch = createEventDispatcher()
    afterUpdate(async () => {
        await tick()
        dispatch('change', value)
    })
</script>

<IconButton toggle bind:pressed={value} {style} on:click>
    <Icon class="material-symbols-outlined" on>{icons.on}</Icon>
    <Icon class="material-symbols-outlined">{icons.off}</Icon>
</IconButton>
