<script context="module">
    export let fullTableData = []
</script>

<script lang="ts">
    import DataTable, { Head, Body, Row, Cell } from '@smui/data-table'
    import { uniqBy } from 'lodash-es'
    import { onMount } from 'svelte'
    export let idKey: string = 'id'
    export let rowKeys: string[] = null
    export let rows = []
    export let headKeys: string[] = null

    export let closeableRows = false
    export let preserveData = false
    export let includeIndex = true

    $: if (preserveData) {
        fullTableData = uniqBy([...fullTableData, ...rows], 'freq')
        rows = [...fullTableData]
    }

    let mounted = false
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
</script>

{#if mounted}
    <DataTable style="width: 100%; user-select:text; ">
        <Head>
            <Row>
                {#if includeIndex}
                    <Cell># {rows.length}</Cell>
                {/if}
                {#each headKeys as key (key)}
                    <Cell>{key}</Cell>
                {/each}
                {#if closeableRows}
                    <Cell
                        ><button
                            class="button is-link"
                            style="background-color: var(--color-danger);"
                            on:click={() => {
                                if (rows.length === 0) return window.createToast('Table is empty', 'warning')
                                rows = fullTableData = []
                                window.createToast('Table cleared', 'danger')
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
                        {#if typeof row[key] !== 'object'}
                            <Cell>{row[key]}</Cell>
                        {:else}
                            <Cell style={row[key]?.style} on:click={row[key]?.cb}>{row[key]?.name}</Cell>
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
{/if}
