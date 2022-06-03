<script>
    import {
        dataTable_avg,
        dataTable,
        expfittedLinesCollectedData,
        avgfittedLineCount,
    } from '../functions/svelteWritables'
    import DataTable, { Head, Body, Row, Cell } from '@smui/data-table'
    import { filter } from 'lodash-es'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'

    export let keepTable = true

    const dataTableHead = ['Filename', 'Frequency (cm-1)', 'Amplitude', 'FWHM', 'Sigma']
    let show_dataTable_only_weighted_averaged = false
    let show_dataTable_only_averaged = false

    $: dataTable_weighted_avg = $dataTable_avg.filter((file) => file.name == 'weighted_mean')
    $: console.log('dataTable', $dataTable)
    $: console.log('dataTable_avg', $dataTable_avg)
    $: console.log('dataTable_weighted_avg', dataTable_weighted_avg)

    function clearTable() {
        $dataTable = $dataTable_avg = []
        $avgfittedLineCount = 0
        $expfittedLinesCollectedData = []
        window.createToast('Table cleared', 'warning')
    }
</script>

<div class="align v-center">
    <div class="notice__div">Frequency table</div>
    <CustomCheckbox bind:value={show_dataTable_only_averaged} label="Only Averaged" />

    <CustomCheckbox bind:value={show_dataTable_only_weighted_averaged} label="Only weighted Averaged" />
    <CustomCheckbox bind:value={keepTable} label="Keep table" />

    <button class="button is-danger" style="margin-left: auto;" on:click={clearTable}>Clear Table</button>
</div>

<div class="dataTable">
    <DataTable
        table$aria-label="felix-tableAriaLabel"
        table$id="felixTable"
        id="felixTableContainer"
        class="tableContainer"
    >
        <Head>
            <Row>
                <Cell style="width: 2em;" />
                {#each dataTableHead as item}
                    <Cell>{item}</Cell>
                {/each}
                <Cell style="width: 2em;" />
            </Row>
        </Head>
        <Body>
            {#if show_dataTable_only_weighted_averaged}
                {#each dataTable_weighted_avg as table, index (table.id)}
                    <Row>
                        <Cell style="width: 2em;">{index}</Cell>
                        <Cell>Line #{index}</Cell>
                        <Cell>{table.freq}</Cell>
                        <Cell>{table.amp}</Cell>
                        <Cell>{table.fwhm}</Cell>
                        <Cell>{table.sig}</Cell>
                        <Cell style="background: #f14668; cursor: pointer;">
                            <i
                                id={table.id}
                                class="material-icons"
                                on:click={(e) => {
                                    dataTable_weighted_avg = filter(
                                        dataTable_weighted_avg,
                                        (tb) => tb.id != e.target.id
                                    )
                                }}>close</i
                            >
                        </Cell>
                    </Row>
                {/each}
            {:else if show_dataTable_only_averaged && !show_dataTable_only_weighted_averaged}
                {#each $dataTable_avg as table, index (table.id)}
                    <Row>
                        <Cell style="width: 2em;">{index}</Cell>
                        <Cell>{table.name}</Cell>
                        <Cell>{table.freq}</Cell>
                        <Cell>{table.amp}</Cell>
                        <Cell>{table.fwhm}</Cell>
                        <Cell>{table.sig}</Cell>
                        <Cell style="background: #f14668; cursor: pointer; width: 2em;">
                            <i
                                id={table.id}
                                class="material-icons"
                                on:click={(e) => {
                                    $dataTable_avg = filter($dataTable_avg, (tb) => tb.id != e.target.id)
                                }}>close</i
                            >
                        </Cell>
                    </Row>
                {/each}
            {:else}
                {#each $dataTable as table, index (table.id)}
                    <Row style="background-color: {table.color};" class={table.className}>
                        <Cell style="width: 2em;">{index}</Cell>
                        <Cell>{table.name}</Cell>
                        <Cell>{table.freq}</Cell>
                        <Cell>{table.amp}</Cell>
                        <Cell>{table.fwhm}</Cell>
                        <Cell>{table.sig}</Cell>
                        <Cell style="background: #f14668; cursor: pointer;">
                            <i
                                id={table.id}
                                class="material-icons"
                                on:click={(e) => {
                                    $dataTable = filter($dataTable, (tb) => tb.id != e.target.id)
                                }}>close</i
                            >
                        </Cell>
                    </Row>
                {/each}
            {/if}
        </Body>
    </DataTable>
</div>

<style>
    .dataTable {
        display: flex;
        justify-content: center;
    }
</style>
