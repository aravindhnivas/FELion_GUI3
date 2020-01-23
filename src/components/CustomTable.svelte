<script>
    import DataTable, {Head, Body, Row, Cell} from '@smui/data-table'

    export let dataTableHead = [], dataTableRow=[], id="table", styleHead="", styleRow="", rowOptions=[], className=""
</script>

<DataTable table$aria-label={className} table$id={id} id="{id}Container">

    <Head style={styleHead}>
        <Row>
            {#each dataTableHead as item}
                <Cell>{item}</Cell>
            {/each}
        </Row>
    </Head>
    <Body>

    {#each dataTableRow as table (table.id)}
        <Row style={styleRow}>
            {#each rowOptions as option (option)}
                <Cell>{table[option]}</Cell>
            {/each}
        </Row>
    {/each}
        
    </Body>
</DataTable>