<script lang="ts">
    import autoAnimate from '@formkit/auto-animate'

    export let prefixId: string = window.getID()
    export let list: { name: string; id: string; active: boolean }[] = []

    let tabCount = 0

    const makeTabActive = (id: string) => {
        list = list.map((tab) => {
            if (tab.id === id) {
                return { ...tab, active: true }
            } else {
                return { ...tab, active: false }
            }
        })
    }

    let ul: HTMLUListElement

    const addTab = async (num = 1, background = false) => {
        for (let i = 0; i < num; i++) {
            const name = `Tab ${tabCount + 1}`
            const id = `${prefixId}-tab-${tabCount}`
            list = [...list, { name, id, active: false }]

            if (!background) makeTabActive(id)
            await tick()
            ul.scrollLeft = ul.scrollWidth - ul.clientWidth
            tabCount++
        }
    }

    const removeTab = (id, index) => {
        const is_it_active_tab = list[index].active
        list = list.filter((item) => item.id !== id)
        if (list.length === 1) tabCount = 1
        if (!is_it_active_tab) return
        makeTabActive(list[index - 1]?.id || list[index]?.id)
    }

    const closeAllTabs = () => {
        if (list.length === 1) return window.createToast('No extra tabs to delete', 'danger')
        makeTabActive(list[0].id)
        list = [list[0]]
        tabCount = 1
    }

    onMount(() => {
        list = []
        tabCount = 0
        addTab()
    })
</script>

<div class="tabs is-toggle m-1 grid">
    <ul class="tabs-ul" use:autoAnimate bind:this={ul}>
        {#each list as item, index (item.id)}
            {@const border = !item.active && index > 0 && index !== list.length ? 'solid 1px darkgrey' : 'none'}
            <li class="tabs-li" class:hvr-grow={!item.active} class:is-active={item.active} style:border-left={border}>
                <!-- svelte-ignore a11y-missing-attribute -->
                <a class="tab">
                    <span
                        class="tab-name"
                        role="presentation"
                        on:click={() => {
                            makeTabActive(item.id)
                        }}>{item.name}</span
                    >
                    {#if index > 0}
                        <button
                            class="delete is-small"
                            on:click={() => {
                                removeTab(item.id, index)
                            }}
                        />
                    {/if}
                </a>
            </li>
        {/each}
        <li class="tabs-li">
            <button class="button is-link ml-2" style="border: none" on:click={() => addTab()}>
                <span class="material-symbols-outlined"> add </span>
            </button>
        </li>
    </ul>
    {#if list.length > 1}
        <button class="tag is-small ml-auto button is-danger" style="border: none" on:click={closeAllTabs}> X </button>
    {/if}
</div>

<style lang="scss">
    .tabs.is-toggle {
        background-color: var(--color-primary-light);

        display: grid;
        grid-template-columns: 1fr auto;
        width: calc(100vw - 5px);
        align-items: center;
        gap: 2em;
        min-width: 0;
        min-height: 0;
        overflow-y: hidden;
        overflow-x: hidden;
        .tabs-ul {
            overflow-x: auto;
            overflow-y: hidden;
        }

        .tabs-li {
            &.is-active .tab {
                border-bottom: solid 1px;
                background-color: whitesmoke;
                opacity: 1;
                .tab-name {
                    color: black;
                }
                .delete {
                    border: solid 1px var(--color-danger);
                }
            }

            .tab {
                gap: 0.5rem;
                border: none;
                opacity: 0.8;
                display: grid;
                min-width: 150px;
                grid-template-columns: 1fr auto;
                cursor: pointer;

                .delete {
                    background-color: white;
                    &:hover {
                        background-color: var(--color-danger);
                    }
                }
            }
        }
    }
</style>
