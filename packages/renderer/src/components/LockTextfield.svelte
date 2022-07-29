<script lang="ts">
    import Textfield from '@smui/textfield'
    import IconButton from '$components/IconButton.svelte'

    export let value: string | number
    export let label: string
    export let browseBtn: boolean = false

    let className: string = ''
    export { className as class }
    let lock = import.meta.env.PROD
</script>

<div class={className}>
    {#if browseBtn}
        <button
            disabled={lock}
            class="button is-link"
            on:click={() => {
                const [result] = window.browse({ dir: false })
                if (!result) return
                value = result
            }}>Browse</button
        >
    {/if}
    <Textfield disabled={lock} bind:value {label} {...$$restProps} />
    <IconButton bind:value={lock} icons={{ on: 'lock', off: 'lock_open' }} />
</div>
