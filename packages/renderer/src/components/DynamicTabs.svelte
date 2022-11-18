<script lang="ts">
    export let prefixId: string = window.getID()
    let list: { name: string; id: string }[] = []

    let activeTab = ''
    let tabCount = 1

    const dispatch = createEventDispatcher()

    const addTab = () => {
        const name = `Tab ${tabCount}`
        const id = `${prefixId}-tab-${tabCount}`

        list = [...list, { name, id }]
        dispatch('tabAdd', { name, id })

        activeTab = name
        dispatch('activeTabChange', { name: activeTab, id })

        tabCount++
    }

    const removeTab = (name, id, index) => {
        list = list.filter((item) => item.id !== id)

        dispatch('tabRemove', { name, id })
        if (activeTab !== name) return

        activeTab = list[index - 1].name
        dispatch('activeTabChange', { name: activeTab, id: list[index - 1].id })

        if (list.length === 1) tabCount = 2
    }
    onMount(addTab)
    onDestroy(() => {
        list = []
    })
</script>

<div class="tabs is-toggle is-toggle-rounded m-1">
    <ul>
        {#each list as { name, id }, index (id)}
            <li class:is-active={activeTab === name}>
                <!-- svelte-ignore a11y-missing-attribute -->
                <a class="tab">
                    <span
                        role="presentation"
                        on:click={() => {
                            activeTab = name
                            dispatch('activeTabChange', {
                                name: activeTab,
                                id: list.find((item) => item.name === activeTab).id,
                            })
                        }}>{name}</span
                    >
                    {#if index > 0}
                        <button
                            class="delete is-small"
                            on:click={() => {
                                removeTab(name, id, index)
                            }}
                        />
                    {/if}
                </a>
            </li>
        {/each}
        <li>
            <button class="button is-link ml-2" style="border: none;" on:click={addTab}>
                <span class="material-symbols-outlined"> add </span>
            </button>
        </li>
    </ul>
</div>

<style lang="scss">
    .tabs.is-toggle {
        background-color: var(--color-primary-light);

        li {
            &:not(:last-child, :first-child, :only-child, .is-active) {
                border-left: solid 1px darkgrey;
            }
            &.is-active .tab {
                border-bottom: solid 1px;
            }

            .tab {
                border: none;
                min-width: 150px;
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 0.5rem;
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
