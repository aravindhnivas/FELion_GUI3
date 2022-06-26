<script>
    import {
        dataTable_avg,
        dataTable,
        expfittedLinesCollectedData,
        avgfittedLineCount,
    } from '../functions/svelteWritables'
    import STable from '$components/STable.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'

    export let keepTable = true

    let show_dataTable_only_weighted_averaged = false
    let show_dataTable_only_averaged = false

    $: dataTable_weighted_avg = $dataTable_avg.filter((file) => file.name == 'weighted_mean')
    $: console.log('dataTable', $dataTable)
    $: console.log('dataTable_avg', $dataTable_avg)
    $: console.log('dataTable_weighted_avg', dataTable_weighted_avg)

    // function clearTable() {
    //     $dataTable = $dataTable_avg = []
    //     $avgfittedLineCount = 0
    //     $expfittedLinesCollectedData = []
    //     window.createToast('Table cleared', 'warning')
    // }

    const rowKeys = ['name', 'freq', 'amp', 'fwhm', 'sig']
    const headKeys = ['Filename', 'Frequency (cm-1)', 'Amplitude', 'FWHM (cm-1)', 'Sigma (cm-1)']
</script>

<div class="align v-center">
    <div class="notice__div">Frequency table</div>
    <CustomCheckbox bind:value={show_dataTable_only_averaged} label="Only Averaged" />

    <CustomCheckbox bind:value={show_dataTable_only_weighted_averaged} label="Only weighted Averaged" />
    <CustomCheckbox bind:value={keepTable} label="Keep table" />
    <!-- <button class="button is-danger" style="margin-left: auto;" on:click={clearTable}>Clear Table</button> -->
</div>

<div class="dataTable">
    <STable rows={$dataTable} {rowKeys} {headKeys} closeableRows={true} preserveData={keepTable} />
</div>

<style>
    .dataTable {
        display: flex;
        justify-content: center;
    }
</style>
