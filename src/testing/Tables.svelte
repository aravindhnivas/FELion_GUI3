<script>
  import DataTable, {Head, Body, Row, Cell} from '@smui/data-table';
</script>

<style>
    section {
        margin: 2em;
    }
</style>

<section>
    <div class="table-container">

        <DataTable table$aria-label="Products">
            <Head>
                <Row>
                <Cell>Name</Cell>
                <Cell>Description</Cell>
                <Cell>Quantity</Cell>
                </Row>
            </Head>
            <Body>
                <Row>
                <Cell>Reds</Cell>
                <Cell>The red ones</Cell>
                <Cell numeric>45</Cell>
                </Row>
                <Row>
                <Cell>Blues</Cell>
                <Cell>The blue ones</Cell>
                <Cell numeric>37</Cell>
                </Row>
                <Row>
                <Cell>Yellows</Cell>
                <Cell>The yellow ones</Cell>
                <Cell numeric>32</Cell>
                </Row>
            </Body>
        </DataTable>
    </div>
</section>