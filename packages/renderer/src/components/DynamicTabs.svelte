<script lang="ts">
    export let prefixId: string = window.getID()
    export let list: { name: string; id: string; active: boolean }[] = []

    let tabCount = 1

    const makeTabActive = (id: string) => {
        list = list.map((tab) => {
            if (tab.id === id) {
                return { ...tab, active: true }
            } else {
                return { ...tab, active: false }
            }
        })
    }

    const addTab = () => {
        const name = `Tab ${tabCount}`
        const id = `${prefixId}-tab-${tabCount}`
        const newTab = { name, id, active: true }
        list = [...list.map((f) => ({ ...f, active: false })), newTab]

        tabCount++
    }

    const removeTab = (id, index) => {
        const is_it_active_tab = list[index].active
        list = list.filter((item) => item.id !== id)

        if (list.length === 1) tabCount = 2
        if (!is_it_active_tab) return
        makeTabActive(list[index - 1]?.id || list[index]?.id)
    }
    onMount(() => {
        list = []
        addTab()
    })
</script>

<div class="tabs is-toggle m-1 grid">
    <ul>
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
            <button class="button is-link ml-2" style="border: none" on:click={addTab}>
                <span class="material-symbols-outlined"> add </span>
            </button>
        </li>
    </ul>
</div>

<style lang="scss">
    .tabs.is-toggle {
        background-color: var(--color-primary-light);
        display: grid;

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
