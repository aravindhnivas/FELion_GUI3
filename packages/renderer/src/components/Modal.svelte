<script>
    import { createEventDispatcher } from 'svelte'

    export let active = false
    export let title = 'Title'
    export let height = '70%'
    export let width = '70%'

    const dispatch = createEventDispatcher()

    const mount = (node) => {
        dispatch('mount', { node })

        return {
            destroy: () => {
                dispatch('close')
                console.log('modal destroyed')
            },
        }
    }
</script>

<svelte:window
    on:keydown={(e) => {
        if (e.key === 'Escape') active = false
    }}
/>

<div class="modal" class:is-active={active} use:mount>
    <div class="modal-background" />

    <div class="modal-card animate__animated animate__fadeIn animate__faster" style:height style:width>
        <header class="modal-card-head">
            <p class="modal-card-title">{title}</p>
            <span
                role="presentation"
                class="delete is-pulled-right"
                on:click={() => {
                    active = false
                    dispatch('closed', { active })
                }}
            />
        </header>

        <section class="modal-card-body background-body" class:scrollable-body={$$slots.body_scrollable__div}>
            <slot name="body_header__div" />
            <slot name="content" style="white-space: pre-wrap;" />
            <slot name="body_scrollable__div" />
        </section>

        <footer class="modal-card-foot">
            <div style="margin-left:auto; display:flex; gap: 1em;">
                <slot name="footerbtn" />
            </div>
        </footer>
    </div>
</div>

<style>
    .scrollable-body {
        display: grid;
        grid-auto-flow: row;
        grid-template-rows: auto 1fr;
        overflow-y: hidden;
    }
    .modal-card-body {
        color: black;
        background-color: #634e96;
    }
    .modal-card-head {
        background-color: #836ac05c;
    }
    .delete {
        background-color: #fafafa;
    }
    .delete:hover {
        background-color: #f14668;
    }
    .modal-card-title {
        margin: 0 !important;
    }
</style>
