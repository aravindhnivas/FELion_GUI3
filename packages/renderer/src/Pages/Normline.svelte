
<script>
    import {
        opoMode,
        graphDiv,
        normMethod,
        Ngauss_sigma,
        baselineFile,
        expfittedLines,
        normMethodDatas,
        felixopoLocation,
        fittedTraceCount,
        
        felixPlotAnnotations,
        expfittedLinesCollectedData,
    }                               from './normline/functions/svelteWritables';
    
    import AddFilesToPlot           from './normline/modals/AddFilesToPlot.svelte';
    import FrequencyTable           from './normline/components/FrequencyTable.svelte';
    import InitFunctionRow          from './normline/widgets/preprocessing/InitFunctionRow.svelte';
    import OPORow                   from './normline/widgets/preprocessing/OPORow.svelte';
    import AdjustInitialGuess       from './normline/modals/AdjustInitialGuess.svelte';
    import TheoryRow                from './normline/widgets/preprocessing/TheoryRow.svelte';
    import GetFileInfoTable         from './normline/widgets/preprocessing/GetFileInfoTable.svelte';
    import WriteFunctionContents    from './normline/widgets/postprocessing/WriteFunctionContents.svelte';
    import ExecuteFunctionContents  from './normline/widgets/postprocessing/ExecuteFunctionContents.svelte';

    import Layout                   from "$components/Layout.svelte"
    import CustomRadio              from '$components/CustomRadio.svelte';
    import {react, deleteTraces}    from 'plotly.js/dist/plotly-basic';
    ///////////////////////////////////////////////////////////////////////

    const filetype="felix"
    const id="Normline"
    
    let fileChecked=[]
    // let toggleBrowser = false;
    let currentLocation = ""
    
    $: felixfiles = fileChecked.map(file=>pathResolve(currentLocation, file))
    $: console.log(`${filetype} currentlocation: \n${currentLocation}`)

    ///////////////////////////////////////////////////////////////////////
    // Theory file

    let show_theoryplot = false
    let theoryLocation = db.get("theoryLocation") || currentLocation
    ///////////////////////////////////////////////////////////////////////

    let graphPlotted = false
    let overwrite_expfit = true
    let writeFile = true
    let OPOfilesChecked = []

    let writeFileName = ""
    let keepTable = true;

    $: plottedFiles = $opoMode ? OPOfilesChecked.map(file=>file.split(".")[0]) || [] : fileChecked.map(file=>file.split(".")[0]) || []
    $: output_namelists = ["averaged", ...plottedFiles, ...addedfiles.map(file=>basename(file)).map(file=>file.split(".")[0])]

    //////// OPO Plot ///////////
    const replot = () => {
        if (graphPlotted) {
            let {data, layout} = $normMethodDatas[$normMethod]
            try {
                react($graphDiv, data, layout, { editable: true })

                $expfittedLines = $felixPlotAnnotations = $expfittedLinesCollectedData = [], $fittedTraceCount = 0
            } catch (err) { console.info(err) }
        }
    }
    // OPO
    
    let OPOLocation = db.get("ofelix_location") || currentLocation
    let opofiles = []

    $: $felixopoLocation = $opoMode ? OPOLocation : currentLocation
    $: $opoMode ? window.createToast("OPO MODE") : window.createToast("FELIX MODE")
    $: $Ngauss_sigma = $opoMode ? 2 : 5

    let addFileModal=false
    let addedFile={}
    let addedfiles = []
    let addedFileCol="0, 1"
    let addedFileScale=1
    let extrafileAdded=0

    $: console.log(`Extrafile added: ${extrafileAdded}`)
   
    function removeExtraFile() {
        for(let i=0; i<extrafileAdded+1; i++) {
            try {
                deleteTraces($graphDiv, [-1])
                
                extrafileAdded--
                addedfiles = addedfiles.slice(0, addedfiles.length-1)
            } catch (err) {console.log("The plot is empty")}
        }
    }

    let fullfiles = []
    let activateConfigModal = false;

    $: $opoMode ? fullfiles = [...opofiles, ...addedfiles, pathResolve(currentLocation, "averaged.felix")] : fullfiles = [...felixfiles, ...addedfiles, pathResolve(currentLocation, "averaged.felix")]

    let modalActivate = false
    let adjustPeakTrigger=false;

</script>

<style>
    .felixPlot > div {margin-bottom: 1em;}
</style>


<!-- Modals -->
<AddFilesToPlot
    {fileChecked}
    bind:addedfiles
    bind:addedFile  
    bind:addedFileCol
    bind:addedFileScale
    bind:extrafileAdded
    bind:active={addFileModal}
/>

<AdjustInitialGuess bind:active={modalActivate} on:save="{()=>adjustPeakTrigger=true}" />

<Layout
    {id}
    {filetype}
    {graphPlotted}
    bind:fileChecked
    bind:currentLocation
    bind:activateConfigModal
    on:markedFile="{(e)=>$baselineFile = e.detail.markedFile}"
>

    <svelte:fragment slot="buttonContainer">
        <InitFunctionRow {removeExtraFile} {felixfiles} normMethod={$normMethod} {theoryLocation}  bind:graphPlotted bind:show_theoryplot />
        <OPORow {removeExtraFile} bind:OPOLocation bind:OPOfilesChecked bind:opofiles  bind:graphPlotted />

        <TheoryRow bind:theoryLocation bind:show_theoryplot  normMethod={$normMethod}  />
        
        <div class="align">
            <CustomRadio on:change={replot} bind:selected={$normMethod} options={["Log", "Relative", "IntensityPerPhoton"]} />

        </div>

    </svelte:fragment>

    <svelte:fragment slot="plotContainer" >

        <GetFileInfoTable {felixfiles} normMethod={$normMethod} />
        <div class="felixPlot" class:hide={!graphPlotted} id="plot_container__div__{filetype}">

            <div class="animated fadeIn graph__div" class:hide={!show_theoryplot} id="exp-theory-plot"></div>
            <div id="bplot" class="graph__div"></div>
            <div id="saPlot" class="graph__div"></div>
            <div id="avgplot" class="graph__div"></div>
            <div class="animated fadeIn graph__div" class:hide={!$opoMode} id="opoplot"></div>
            <div class="animated fadeIn graph__div" class:hide={!$opoMode} id="opoSA"></div>

            <div class="animated fadeIn graph__div" class:hide={!$opoMode} id="opoRelPlot"></div>
        
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer_functions" >

        <WriteFunctionContents on:addfile="{()=>{addFileModal=true}}" on:removefile={removeExtraFile} {output_namelists} bind:writeFileName bind:writeFile bind:overwrite_expfit />
        <ExecuteFunctionContents {addedFileScale} {addedFileCol} normMethod={$normMethod} {writeFileName} {writeFile} {overwrite_expfit} {fullfiles}  bind:modalActivate bind:adjustPeakTrigger />

    </svelte:fragment>

    <svelte:fragment slot="plotContainer_reports">
        <FrequencyTable bind:keepTable/>
    </svelte:fragment>


</Layout>