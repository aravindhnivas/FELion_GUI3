<script lang="ts">
    import DataTable, { Head, Body, Row, Cell } from '@smui/data-table'
    import { orderBy, uniqBy } from 'lodash-es'
    import { createEventDispatcher, onMount } from 'svelte'
    import IconButton, { Icon } from '@smui/icon-button'
    import FileReadAndLoad from '$components/FileReadAndLoad.svelte'
    export let idKey: string = 'id'
    export let rowKeys: string[] = null
    export let rows = []
    export let headKeys: string[] = null
    export let closeableRows = false
    export let includeIndex = true

    export let editable = false
    export let sortable = false
    export let configDir: string = null
    export let options_filter: string = '.json'

    let mounted = false
    // $: console.log(rows)
    onMount(() => {
        rows = uniqBy(rows, idKey)
        if (rowKeys === null) {
            rowKeys = Object.keys(rows[0])
        }
        if (headKeys === null) {
            headKeys = Object.keys(rows[0])
        }
        mounted = true
    })

    let sortToggle = {}
    rowKeys.forEach((key) => (sortToggle[key] = false))
    const sortTable = (key) => {
        console.log({ key })
        rows = orderBy(rows, key, sortToggle[key] ? 'asc' : 'desc')
    }

    const dispatch = createEventDispatcher()
</script>

{#if mounted}
    <div class="align">
        {#if configDir}
            <FileReadAndLoad bind:dataToSave={rows} {configDir} singleFilemode={true} {options_filter} />
        {/if}
        <DataTable style="width: 100%; user-select:text;">
            <Head>
                <Row>
                    {#if includeIndex}
                        <Cell># {rows.length}</Cell>
                    {/if}
                    {#each headKeys as key, i (key)}
                        <Cell on:click={() => sortTable(rowKeys[i])}>
                            <div class="header_cell has-background-link">
                                <span>{key}</span>
                                {#if sortable}
                                    <IconButton toggle bind:pressed={sortToggle[rowKeys[i]]}>
                                        <Icon class="material-icons">arrow_downward</Icon>
                                        <Icon class="material-icons" on>arrow_upward</Icon>
                                    </IconButton>
                                {/if}
                            </div>
                        </Cell>
                    {/each}
                    {#if closeableRows}
                        <Cell
                            ><button
                                class="button is-link"
                                style="background-color: var(--color-danger);"
                                on:click={() => {
                                    if (rows.length === 0) return window.createToast('Table is empty', 'warning')
                                    rows = []
                                    window.createToast('Table cleared', 'danger')
                                    dispatch('tableCleared')
                                }}>Clear Table</button
                            ></Cell
                        >
                    {/if}
                </Row>
            </Head>

            <Body>
                {#each rows as row, index (row[idKey])}
                    <Row>
                        {#if includeIndex}
                            <Cell>{index + 1}</Cell>
                        {/if}
                        {#each rowKeys as key (key)}
                            {#if typeof row[key] === 'object'}
                                <Cell style={row[key]?.style} on:click={row[key]?.cb}>{row[key]?.name}</Cell>
                            {:else}
                                <Cell>
                                    {#if editable}
                                        <input type="text" bind:value={row[key]} style="color: black; width: 100%;" />
                                    {:else}
                                        {row[key]}
                                    {/if}
                                </Cell>
                            {/if}
                        {/each}
                        {#if closeableRows}
                            <Cell style="width: 5em;">
                                <button
                                    style="background-color: var(--color-danger);"
                                    class="button is-danger"
                                    on:click={() => {
                                        rows = rows.filter((r) => r[idKey] !== row[idKey])
                                    }}
                                >
                                    X
                                </button>
                            </Cell>
                        {/if}
                    </Row>
                {/each}
            </Body>
        </DataTable>
    </div>
{/if}

<style>
    .header_cell {
        display: flex;
        border-radius: 1em;
        align-items: center;
        justify-content: center;
    }
</style>
