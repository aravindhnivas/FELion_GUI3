<script>
    import { onDestroy } from 'svelte'
    import { mainPreModal } from '$src/sveltewritables'
    import FlatList from 'svelte-flatlist'

    let active = false
    function openModal() {
        active = true
        $mainPreModal.open = false
    }

    $: if ($mainPreModal.open) {
        openModal()
    }
    $: console.log($mainPreModal)
    let headerBackground = '#836ac05c'
    $: if (active) {
        headerBackground = $mainPreModal.type === 'danger' ? '#f14668' : '#836ac05c'
    }

    function handleKeydown(event) {
        const key = event.key.toLowerCase()
        if (key === 'escape') {
            active = false
            return
        }
        const { ctrlKey, shiftKey } = event
        if (ctrlKey && shiftKey) {
            if (key === 'e') {
                active = !active
            }
        }
    }

    onDestroy(() => (active = false))
</script>

<svelte:window on:keydown={handleKeydown} />

{#if active}
    <FlatList
        on:close={() => {
            active = false
        }}
        bind:visible={active}
        style={{
            bgColor: '#eee',
            handle: {
                fgColor: 'white',
                height: '2rem',
                bgColor: headerBackground,
            },
        }}
    >
        <div class="contents">
            <h1 style="text-align: center;">
                {$mainPreModal.type === 'danger' ? 'Error occured' : 'Output'}
            </h1>
            <hr />
            <div style="user-select: text; white-space: pre-wrap;">
                {#if $mainPreModal.content instanceof Error}
                    {$mainPreModal.content.stack}
                {:else}
                    {$mainPreModal.content}
                {/if}
            </div>
        </div>
    </FlatList>
{/if}

<style lang="scss">
    .contents {
        * {
            color: black;
        }
    }
</style>
