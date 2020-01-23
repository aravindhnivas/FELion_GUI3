<script>
    import DataTable, {Head, Body, Row, Cell} from '@smui/data-table'

    export let dataTableHead = [], id="table", styleHead=""
</script>

<DataTable table$aria-label="{id}-tableAriaLabel" table$id={id} id="{id}Container">

    <Head style={styleHead}>
        <Row>
            {#each dataTableHead as item}
                <Cell>{item}</Cell>
            {/each}
        </Row>
    </Head>
    <Body>

    <slot ><!-- optional fallback --></slot>
        
    </Body>
</DataTable>