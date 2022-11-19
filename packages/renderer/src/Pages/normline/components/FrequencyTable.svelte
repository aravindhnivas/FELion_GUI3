<script lang="ts">
    import {
        dataTable,
        normMethod,
        dataTable_avg,
        frequencyDatas,
        fitted_data,
        avgfittedLineCount,
        expfittedLinesCollectedData,
        felixopoLocation,
    } from '../functions/svelteWritables'
    import STable from '$components/STable.svelte'

    $: if ($fitted_data?.[uniqueID]?.[$normMethod]) {
        $frequencyDatas[uniqueID] = $fitted_data[uniqueID][$normMethod]
    }

    const uniqueID = getContext<string>('uniqueID')
    function tableCleanup() {
        $fitted_data[uniqueID] = {}
        $frequencyDatas[uniqueID] = []
        $dataTable[uniqueID] = []
        $dataTable_avg[uniqueID] = []
        $avgfittedLineCount = 0
        $expfittedLinesCollectedData = []
    }
    const rowKeys = ['name', 'freq', 'amp', 'fwhm', 'sig']
    const headKeys = ['Filename', 'Frequency', 'Intensity', 'FWHM', 'Sigma']

    $: felixOpoDatLocation = window.path.resolve($felixopoLocation[uniqueID], '../EXPORT')
    onMount(() => {
        frequencyDatas.init(uniqueID)
        fitted_data.init(uniqueID)
        dataTable.init(uniqueID)
        dataTable_avg.init(uniqueID)
        return () => {
            frequencyDatas.remove(uniqueID)
            fitted_data.remove(uniqueID)
            dataTable.remove(uniqueID)
            dataTable_avg.init(uniqueID)
        }
    })
</script>

<div class="notice__div">Frequency table</div>
<STable
    rows={$frequencyDatas[uniqueID]}
    {rowKeys}
    {headKeys}
    closeableRows={true}
    on:tableCleared={tableCleanup}
    sortable={true}
    configDir={felixOpoDatLocation}
    options_filter=".felix.table.json"
/>
