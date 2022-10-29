<script lang="ts">
    import Textfield from '@smui/textfield'
    import IconButton from '$components/IconButton.svelte'
    import { createEventDispatcher } from 'svelte'
    export let value: string | number
    export let label: string = ''
    export let browseBtn: boolean = true
    export let dir: boolean = true
    export let filetype: string = ''
    export let lock: boolean | null = null
    export let type: string = 'text'
    export let updateMode: boolean | null = null

    export let style: string = ''
    let className: string = ''
    export { className as class }

    const dispatch = createEventDispatcher()
    const update = async (e: { currentTarget: HTMLElement }) => {
        e.currentTarget.classList.add('animate__rotateIn')
        dispatch('update')
    }
</script>

<div class={className} {style}>
    {#if browseBtn}
        <button
            disabled={lock ?? false}
            class="button is-link"
            on:click={() => {
                const [result] = window.browse({ dir, filetype })
                if (!result) return
                value = result
                dispatch('fileupdate', result)
            }}>Browse</button
        >
    {/if}
    <Textfield disabled={lock ?? false} bind:value {label} {type} />

    {#if updateMode !== null}
        <i
            class="material-symbols-outlined animate__animated animate__faster"
            on:animationend={({ currentTarget }) => {
                currentTarget.classList.remove('animate__rotateIn')
            }}
            on:click={update}
        >
            refresh
        </i>
    {/if}

    {#if lock !== null}
        <IconButton bind:value={lock} icons={{ on: 'lock', off: 'lock_open' }} />
    {/if}
    <slot />
</div>
