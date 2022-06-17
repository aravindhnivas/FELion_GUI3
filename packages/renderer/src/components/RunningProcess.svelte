<script>
    import { running_processes } from '$src/sveltewritables'
    import DataTable, { Head, Body, Row, Cell } from '@smui/data-table'
    $: console.log($running_processes)
</script>

<DataTable table$aria-label="current processes list" style="width: 100%;">
    <Head>
        <Row>
            <Cell>PID</Cell>
            <Cell>pyfile</Cell>
            <Cell />
        </Row>
    </Head>

    <Body>
        {#each $running_processes as { pid, pyfile, kill: killProcess } (pid)}
            <Row>
                <Cell>{pid}</Cell>
                <Cell>{pyfile}</Cell>
                <Cell
                    ><button class="button is-danger" style:background="var(--color-danger)" on:click={killProcess}
                        >X</button
                    ></Cell
                >
            </Row>
        {/each}
    </Body>
</DataTable>

<br />
<div style="height: 1rem;" />
