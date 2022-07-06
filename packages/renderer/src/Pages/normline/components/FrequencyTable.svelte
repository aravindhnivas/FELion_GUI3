<script>
    import {
        dataTable,
        normMethod,
        dataTable_avg,
        frequencyDatas,
        avgfittedLineCount,
        expfittedLinesCollectedData,
        felixOpoDatLocation,
    } from '../functions/svelteWritables'

    import STable from '$components/STable.svelte'
    import { fitted_data } from '../functions/NGauss_fit'

    $: if ($fitted_data?.[$normMethod]) {
        $frequencyDatas = $fitted_data?.[$normMethod]
    }
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
<STable
    rows={$frequencyDatas}
    {rowKeys}
    {headKeys}
    closeableRows={true}
    on:tableCleared={tableCleanup}
    sortable={true}
    configDir={$felixOpoDatLocation}
    options_filter=".felix.table.json"
/>
