<script>
    import DataTable, {Head, Body, Row, Cell} from '@smui/data-table';
    import Checkbox from '@smui/checkbox';
    export let head, rows, id;
    let keys = Object.keys(rows)

</script>


 <div style="display: flex; justify-content: center;">
    <DataTable table$aria-label="{id}-tableAriaLabel" table$id={id} id="{id}Container">
    <Head >

        <Row>
            {#each head as item}
                <Cell>{item}</Cell>

            {/each}
        </Row>
    </Head>
    <Body>
        {#each rows as row, index (row.id)}
            <Row>
                {#each rowItems as item, index (row.id2)}
                    <Cell>{item[keys[index]]}</Cell>
                {/each}
            </Row>
        {/each}
    </Body>
    </DataTable>
 </div>