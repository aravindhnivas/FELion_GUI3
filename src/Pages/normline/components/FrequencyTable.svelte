
<script>
    import DataTable, {Head, Body, Row, Cell} from '@smui/data-table';
    import {Icon} from '@smui/icon-button';
    import {createToast} from "../../../components/Layout.svelte"
    import CustomCheckbox from '../../../components/CustomCheckbox.svelte';
    export let dataTable_avg, dataTable, keepTable=true, line_index_count=0, lineData_list = []

    const dataTableHead = ["Filename", "Frequency (cm-1)", "Amplitude", "FWHM", "Sigma"]

    let show_dataTable_only_weighted_averaged = false, show_dataTable_only_averaged = false
    $: dataTable_weighted_avg = dataTable_avg.filter(file=> file.name == "weighted_mean")
    $: console.log("dataTable", dataTable)
    $: console.log("dataTable_avg", dataTable_avg)

    $: console.log("dataTable_weighted_avg", dataTable_weighted_avg)
</script>


<style>
    .dataTable { display: flex; justify-content: center; }
    .notification {width: 100%; border: 1px solid;}

</style>

<div class="content">
    <div class="title notification is-link">Frequency table</div>
    <CustomCheckbox bind:selected={show_dataTable_only_averaged} label="Only Averaged" />

    <CustomCheckbox bind:selected={show_dataTable_only_weighted_averaged} label="Only weighted Averaged" />
    <CustomCheckbox bind:selected={keepTable} label="Keep table" />

    <button class="button is-danger is-pulled-right" on:click="{()=>{dataTable=dataTable_avg=[]; line_index_count=0; lineData_list=[]; createToast("Table cleared", "warning")}}">Clear Table</button>
</div>

 <div class="dataTable" >
    <DataTable table$aria-label="felix-tableAriaLabel" table$id="felixTable" id="felixTableContainer" class="tableContainer">

        <Head >
            <Row>
                <Cell style="width: 2em;"></Cell>
                {#each dataTableHead as item}
                    <Cell>{item}</Cell>
                {/each}
                <Cell style="width: 2em;"></Cell>
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
                            <Icon id="{table.id}" class="material-icons" 
                                on:click="{(e)=> {dataTable_weighted_avg = window._.filter(dataTable_weighted_avg, (tb)=>tb.id != e.target.id)}}">close</Icon>
                        </Cell>
                    </Row>
                {/each}
            {:else if show_dataTable_only_averaged && !show_dataTable_only_weighted_averaged}
                {#each dataTable_avg as table, index (table.id)}
                    <Row>
                        <Cell style="width: 2em;">{index}</Cell>
                        <Cell>{table.name}</Cell>
                        <Cell>{table.freq}</Cell>
                        <Cell>{table.amp}</Cell>
                        <Cell>{table.fwhm}</Cell>
                        <Cell>{table.sig}</Cell>
                        <Cell style="background: #f14668; cursor: pointer; width: 2em;">
                            <Icon id="{table.id}" class="material-icons" 
                                on:click="{(e)=> {dataTable_avg = window._.filter(dataTable_avg, (tb)=>tb.id != e.target.id)}}">close</Icon>
                        </Cell>
                    </Row>
                {/each}
            {:else}

                {#each dataTable as table, index (table.id)}
                    <Row style="background-color: {table.color};" class={table.className}>
                        <Cell style="width: 2em;">{index}</Cell>
                        <Cell>{table.name}</Cell>
                        <Cell>{table.freq}</Cell>
                        <Cell>{table.amp}</Cell>
                        <Cell>{table.fwhm}</Cell>
                        <Cell>{table.sig}</Cell>
                        <Cell style="background: #f14668; cursor: pointer;">
                            <Icon id="{table.id}" class="material-icons" 
                                on:click="{(e)=> {dataTable = window._.filter(dataTable, (tb)=>tb.id != e.target.id)}}">close</Icon>
                        </Cell>
                    </Row>
                {/each}
            {/if}
        </Body>

    </DataTable>
</div>