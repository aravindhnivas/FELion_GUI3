<script>
    import {
        dataTable,
        normMethod,
        dataTable_avg,
        frequencyDatas,
        avgfittedLineCount,
        expfittedLinesCollectedData,
    } from '../functions/svelteWritables'
    import STable from '$components/STable.svelte'
    // import CustomCheckbox from '$components/CustomCheckbox.svelte'
    import { fitted_data } from '../functions/NGauss_fit'

    // export let keepTable = true

    $: if ($fitted_data?.[$normMethod]) {
        $frequencyDatas = $fitted_data?.[$normMethod]
    }
    // let averageMode = false
    function tableCleanup() {
        $fitted_data = null
        $frequencyDatas = []
        $dataTable = $dataTable_avg = []
        $avgfittedLineCount = 0
        $expfittedLinesCollectedData = []
    }
    const rowKeys = ['name', 'freq', 'amp', 'fwhm', 'sig']
    const headKeys = ['Filename', 'Frequency', 'Intensity', 'FWHM', 'Sigma']
</script>

<div class="notice__div">Frequency table</div>
<!-- <div class="align v-center">
    <div class="notice__div">Frequency table</div>
    <CustomCheckbox bind:value={averageMode} label="Only Averaged" />
    <CustomCheckbox bind:value={keepTable} label="Keep table" />
</div> -->

<!-- <div class="dataTable"> -->
<STable
    rows={$frequencyDatas}
    {rowKeys}
    {headKeys}
    closeableRows={true}
    on:tableCleared={tableCleanup}
    sortable={true}
/>
<!-- </div> -->
<!-- 
<style>
    .dataTable {
        display: flex;
        justify-content: center;
    }
</style> -->
