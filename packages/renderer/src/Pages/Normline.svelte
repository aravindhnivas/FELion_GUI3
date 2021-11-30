
<script>
    import {
        opoMode, normMethodDatas, Ngauss_sigma, felixopoLocation, felixPlotAnnotations, 
        expfittedLines, expfittedLinesCollectedData, fittedTraceCount, graphDiv, normMethod,
        felixConfigDB, baselineFile
    } from './normline/functions/svelteWritables';
    import Layout from "$components/Layout.svelte"
    import CustomRadio from '$components/CustomRadio.svelte';
    // import ReportLayout from '$components/ReportLayout.svelte';
    import {tick} from "svelte";
    import AddFilesToPlot from './normline/modals/AddFilesToPlot.svelte';

    import FrequencyTable from './normline/components/FrequencyTable.svelte';
    import InitFunctionRow from './normline/widgets/preprocessing/InitFunctionRow.svelte';
    import OPORow from './normline/widgets/preprocessing/OPORow.svelte';



    
    import AdjustInitialGuess from './normline/modals/AdjustInitialGuess.svelte';
    import TheoryRow from './normline/widgets/preprocessing/TheoryRow.svelte';
    import GetFileInfoTable from './normline/widgets/preprocessing/GetFileInfoTable.svelte';
    import WriteFunctionContents from './normline/widgets/postprocessing/WriteFunctionContents.svelte';
    import ExecuteFunctionContents from './normline/widgets/postprocessing/ExecuteFunctionContents.svelte';
    import {init_tour_normline} from './normline/initTour';
    import Textfield from '@smui/textfield';
    
    ///////////////////////////////////////////////////////////////////////

    const filetype="felix", id="Normline"
    let fileChecked=[], toggleBrowser = false;
    let currentLocation = db.get(`${filetype}_location`) || ""
    $: felixfiles = fileChecked.map(file=>pathResolve(currentLocation, file))
    $: console.log(`${filetype} currentlocation: \n${currentLocation}`)
    ///////////////////////////////////////////////////////////////////////
    // const dispatch = createEventDispatcher();
    // Theory file
    let show_theoryplot = false
    let theoryLocation = db.get("theoryLocation") || currentLocation

    ///////////////////////////////////////////////////////////////////////
    let graphPlotted = false, overwrite_expfit = false, writeFile = false

    let OPOfilesChecked = []
    $: plottedFiles = $opoMode ? OPOfilesChecked.map(file=>file.split(".")[0]) || [] : fileChecked.map(file=>file.split(".")[0]) || []
    $: output_namelists = ["averaged", ...plottedFiles, ...addedfiles.map(file=>basename(file)).map(file=>file.split(".")[0])]

    let writeFileName = ""
    let keepTable = true;

    //////// OPO Plot ///////////
    window.getID = () => Math.random().toString(32).substring(2)
    
    const replot = () => {
        if (graphPlotted) {
            let {data, layout} = $normMethodDatas[$normMethod]
            try {
                window.Plotly.react($graphDiv, data, layout, { editable: true })
                $expfittedLines = $felixPlotAnnotations = $expfittedLinesCollectedData = [], $fittedTraceCount = 0
            } catch (err) {
            }
        }
    }


    // OPO
    
    let OPOLocation = db.get("ofelix_location") || currentLocation
    let opofiles = []
    $: $felixopoLocation = $opoMode ? OPOLocation : currentLocation
    $: $opoMode ? window.createToast("OPO MODE", "warning") : window.createToast("FELIX MODE")
    $: $Ngauss_sigma = $opoMode ? 2 : 5
    let addFileModal=false, addedFileCol="0, 1", addedFile={}, addedFileScale=1, addedfiles = [], extrafileAdded=0

    $: console.log(`Extrafile added: ${extrafileAdded}`)
   
    function removeExtraFile() {
        for(let i=0; i<extrafileAdded+1; i++) {
            try {
                window.Plotly.deleteTraces($graphDiv, [-1])
                extrafileAdded--
                addedfiles.pop()
            } catch (err) {console.log("The plot is empty")}
        }

    }

    let fullfiles = []
    let activateConfigModal = false;
    $: $opoMode ? fullfiles = [...opofiles, ...addedfiles, pathResolve(currentLocation, "averaged.felix")] : fullfiles = [...felixfiles, ...addedfiles, pathResolve(currentLocation, "averaged.felix")]

    const init_tour = async () => {
        if (!toggleBrowser) {toggleBrowser = true; await sleep(600)} // Filebrowser toggling and its animation time to appear

        await tick() // For all the reactive components to render
        init_tour_normline({filetype})
    }
    let fdelta = $felixConfigDB.get("fdelta") || 0.5
    let odelta = $felixConfigDB.get("odelta") || 0.001

    let scalingBin = $felixConfigDB.get("scalingBin") || 0.001
    let updateConfig = false
    async function configSave() {
        $felixConfigDB.set("fdelta", fdelta)
        $felixConfigDB.set("odelta", odelta)
        $felixConfigDB.set("scalingBin", scalingBin)
        updateConfig = true;
        console.log("Config file saved", $felixConfigDB.JSON())
        await tick()
        updateConfig = false
        console.log("Config updated")
    }

    let modalActivate = false, adjustPeakTrigger=false;

</script>

<style>
    .felixPlot > div {margin-bottom: 1em;}
</style>


<!-- Modals -->
<AddFilesToPlot {fileChecked} bind:extrafileAdded bind:active={addFileModal} bind:addedFileCol bind:addedFileScale bind:addedfiles bind:addedFile  />
<AdjustInitialGuess bind:active={modalActivate} on:save="{()=>adjustPeakTrigger=true}" />
<!-- Layout -->
<Layout  {filetype} {graphPlotted} {id} bind:currentLocation bind:fileChecked bind:toggleBrowser on:tour={init_tour} bind:activateConfigModal on:configSave={configSave} on:markedFile="{(e)=>$baselineFile = e.detail.markedFile}">

    <svelte:fragment slot="buttonContainer">
        <InitFunctionRow {removeExtraFile} {opofiles} {felixfiles} normMethod={$normMethod} {theoryLocation}  bind:graphPlotted bind:show_theoryplot {updateConfig} />

        <OPORow {removeExtraFile} bind:OPOLocation bind:OPOfilesChecked bind:opofiles  bind:graphPlotted {updateConfig} />
        <TheoryRow bind:theoryLocation bind:show_theoryplot  normMethod={$normMethod} {updateConfig} />
        <div class="align">

            <CustomRadio on:change={replot} bind:selected={$normMethod} options={["Log", "Relative", "IntensityPerPhoton"]}/>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer" >

        <!-- Get file info functions -->
        <GetFileInfoTable {felixfiles} normMethod={$normMethod} />
        
        <!-- Plots container -->
        <div class="felixPlot" id="plot_container__div__{filetype}">
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

        <!-- Write function buttons -->

        <WriteFunctionContents on:addfile="{()=>{addFileModal=true}}" on:removefile={removeExtraFile} {output_namelists} bind:writeFileName bind:writeFile bind:overwrite_expfit />
        <!-- Execute function buttons -->
        <ExecuteFunctionContents {addedFileScale} {addedFileCol} normMethod={$normMethod} {writeFileName} {writeFile} {overwrite_expfit} {fullfiles}  bind:modalActivate bind:adjustPeakTrigger />

    </svelte:fragment>

    <svelte:fragment slot="plotContainer_reports">
        <FrequencyTable bind:keepTable/>
    </svelte:fragment>

    <svelte:fragment slot="config">

        <div class="align" on:configSave={()=>console.log("Config save triggered")}>
            <Textfield bind:value={fdelta} label="FELIX delta steps" varient="outlined" input$type="number" input$min="0" input$step="1e-5"/>
            <Textfield bind:value={odelta} label="OPO delta steps" varient="outlined" input$type="number" input$min="0" input$step="1e-5"/>
            <Textfield bind:value={scalingBin} label="Theory scaling steps" varient="outlined" input$type="number" input$min="0" input$step="1e-5" />
        </div>
    </svelte:fragment>

</Layout>