<script lang="ts">
    import DataTable, { Head, Body, Row, Cell } from '@smui/data-table'

    export let idKey: string = 'id'
    export let rowKeys: string[] = null
    export let rows = []
    export let headKeys: string[] = null
</script>

<DataTable style="width: 100%;">
    <Head>
        <Row>
            {#each headKeys || rowKeys as key (key)}
                <Cell>{key}</Cell>
            {/each}
        </Row>
    </Head>

    <Body>
        {#each rows as row (row[idKey])}
            <Row>
                {#each rowKeys as key (key)}
                    {#if typeof row[key] !== 'object'}
                        <Cell>{row[key]}</Cell>
                    {:else}
                        <Cell style={row[key]?.style} on:click={row[key]?.cb}>{row[key]?.name}</Cell>
                    {/if}
                {/each}
            </Row>
        {/each}
    </Body>
</DataTable>
