
<script>

    // IMPORTING Modules
    import {felixIndex, felixPeakTable, felixOutputName, opoMode, dataTable, dataTable_avg, normMethodDatas, Ngauss_sigma, felixopoLocation, felixPlotAnnotations, expfittedLines, expfittedLinesCollectedData, fittedTraceCount, graphDiv} from './normline/functions/svelteWritables';
    
    import Layout, {createToast} from "../components/Layout.svelte"
    
    import { fade } from 'svelte/transition'
    import CustomRadio from '../components/CustomRadio.svelte';
    import ReportLayout from '../components/ReportLayout.svelte';
    import {onMount, tick} from "svelte"

    import AdjustInitialGuess from './normline/modals/AdjustInitialGuess.svelte';
    import AddFilesToPlot from './normline/modals/AddFilesToPlot.svelte';
    import FrequencyTable from './normline/components/FrequencyTable.svelte';

    import InitFunctionRow from './normline/widgets/preprocessing/InitFunctionRow.svelte';
    
    import OPORow from './normline/widgets/preprocessing/OPORow.svelte';
    import TheoryRow from './normline/widgets/preprocessing/TheoryRow.svelte';
    import GetFileInfoTable from './normline/widgets/preprocessing/GetFileInfoTable.svelte';
    import WriteFunctionContents from './normline/widgets/postprocessing/WriteFunctionContents.svelte';
    import ExecuteFunctionContents from './normline/widgets/postprocessing/ExecuteFunctionContents.svelte';
    import {init_tour_normline} from './normline/initTour';

    import {get_details_func} from './normline/functions/get_details';
    
    import {savefile, loadfile} from './normline/functions/misc';
    import {computePy_func} from './normline/functions/computePy';

    ///////////////////////////////////////////////////////////////////////

    const filetype="felix", id="Normline"

    let fileChecked=[], delta=1, toggleBrowser = false;
    
    let currentLocation = localStorage[`${filetype}_location`] || ""
    $: felixfiles = fileChecked.map(file=>path.resolve(currentLocation, file))

    $: console.log(`${filetype} currentlocation: \n${currentLocation}`)
    
    ///////////////////////////////////////////////////////////////////////

    // Theory file
    let sigma = 20, scale=1, show_theoryplot = false
    let theoryLocation = localStorage["theoryLocation"] || currentLocation
    let theoryfiles = [];

    ///////////////////////////////////////////////////////////////////////
    let openShell = false;
    $: console.log("Open Shell: ", filetype, openShell)

    let felix_normMethod = "Relative", NGauss_fit_args = {};

    let graphPlotted = false, overwrite_expfit = false, writeFile = false
    $: console.log("Trace length: ", $fittedTraceCount)

    let OPOfilesChecked = []
    $: plottedFiles = $opoMode ? OPOfilesChecked.map(file=>file.split(".")[0]) || [] : fileChecked.map(file=>file.split(".")[0]) || []

    $: output_namelists = ["averaged", ...plottedFiles, ...addedfiles.map(file=>path.basename(file)).map(file=>file.split(".")[0])]
    let writeFileName = ""
    
    let boxSelected_peakfinder = false;
    let keepTable = true;

    //////// OPO Plot ///////////
    window.getID = () => Math.random().toString(32).substring(2)

    const replot = () => {
        if (graphPlotted) {

            let {data, layout} = $normMethodDatas[normMethod]
            Plotly.react("avgplot",data, layout, { editable: true })
            $expfittedLines = $felixPlotAnnotations = $expfittedLinesCollectedData = [], $fittedTraceCount = 0
        }

    }

    function plotData({e=null, filetype="felix", general=null, tkplot="run"}={}){
        let pyfile="", args;
        
        let expfit_args = [], find_peaks_args = {}
        if (filetype == "general") {
            const {pyfile, args} = general
            computePy_func({pyfile, args, general:true, openShell})
            .catch(err=>{preModal.modalContent = err;  preModal.open = true})
            return;
        }

        
        switch (filetype) {

            case "addfile":

                if(addedFile.files < 1) return createToast("No files selected", "danger")
                addedFile["col"] = addedFileCol, addedFile["N"] = fileChecked.length + extrafileAdded

                addedFile["scale"] = addedFileScale
                pyfile="addTrace.py" , args=[JSON.stringify(addedFile)]

                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    addFileModal = false
                    Plotly.addTraces($graphDiv, dataFromPython)
                    extrafileAdded += addedfiles.length
                }).catch(err=>{preModal.modalContent = err;  preModal.open = true})
                break;

            case "get_details":
                if(felixfiles.length<1) return createToast("No files selected", "danger")
                pyfile="getfile_details.py", args=[JSON.stringify({files:$opoMode?opofiles : felixfiles, normMethod})]

                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{ get_details_func({dataFromPython}) })

                .catch(err=>{preModal.modalContent = err;  preModal.open = true})
                
                break;

            default:
                break;
        }

    }

    
    // OPO
    let OPOLocation = localStorage["opoLocation"] || currentLocation
    let opofiles = []

    
    $: normMethod = $opoMode ? "Log" : felix_normMethod
    $: $felixopoLocation = $opoMode ? OPOLocation : currentLocation
    

    $: $opoMode ? createToast("OPO MODE") : createToast("FELIX MODE")
    $: $Ngauss_sigma = $opoMode ? 2 : 5
    let addFileModal=false, addedFileCol="0, 1", addedFile={}, addedFileScale=1, addedfiles = [], extrafileAdded=0
    
    $: console.log(`Extrafile added: ${extrafileAdded}`)
   
    function removeExtraFile() {
        for(let i=0; i<extrafileAdded; i++) {

            try {Plotly.deleteTraces($graphDiv, [-1])}
            catch (err) {console.log("The plot is empty")}
        }
        
        extrafileAdded = 0, addedfiles = []
    }


    let fullfiles = []
    
    $: $opoMode ? fullfiles = [...opofiles, ...addedfiles, path.resolve(currentLocation, "averaged.felix")] : fullfiles = [...felixfiles, ...addedfiles, path.resolve(currentLocation, "averaged.felix")]

    const init_tour = async () => {
        if (!toggleBrowser) {toggleBrowser = true; await sleep(600)} // Filebrowser toggling and its animation time to appear
        await tick() // For all the reactive components to render
        init_tour_normline({filetype})

    }

    const includePlotsInReport = [

        {id: "bplot", include:true, label:"Baseline"}, {id:"saPlot", include:false, label:"SA-Pow"}, 
        {id:"avgplot", include:false, label:"Normalised Spectrum"}, {id:"exp-theory-plot", include:false, label:"Exp-Theory plot"}, 
        {id:"opoplot", include:false, label:"OPO: Baseline"}, {id:"opoSA", include:false, label:"OPO: SA-pow"}, 
        {id:"opoRelPlot", include:false, label:"OPO: Normalised Spectrum"}
    ]

    const includeTablesInReports = [
        {id:"felixTable", include:true, label:"Freq. table"}, {id:"felix_filedetails_table", include:false, label:"File info table"}
    ]

    $: datlocation = path.resolve($felixopoLocation, "../EXPORT")
    $: datfiles = fs.existsSync(datlocation) ? fs.readdirSync(datlocation).filter(f=>f.endsWith(".dat")).map(f=>f={name:f, id:getID()}) : [{name:"", id:getID()}]
    $: calcfiles = fs.existsSync(theoryLocation) ? fs.readdirSync(theoryLocation).map(f=>f={name:f, id:getID()}) : [{name:"", id:getID()}]

    $: felixPlotCheckboxes = [
            {label:"DAT file", options:datfiles, selected:[], style:"width:100%;", id:getID()},
            {label:"Fundamentals", options:calcfiles, selected:[], style:"width:25%;", id:getID()},
            {label:"Overtones", options:calcfiles, selected:[], style:"width:25%;", id:getID()},

            {label:"Combinations", options:calcfiles, selected:[], style:"width:25%;", id:getID()},
        ]
    let preModal = {};

    $: console.log(`$opoMode: ${$opoMode}`)

    onMount(()=>{  console.log("Normline mounted") })

    $: console.log(`graphDiv: ${$graphDiv}`)

</script>


<style>
    .hide {display: none;}
    .felixPlot > div {margin-bottom: 1em;}
    .plotSlot > div { width: calc(100% - 1em); margin-top: 1em; }
</style>

<!-- Modals -->
<AddFilesToPlot bind:active={addFileModal} bind:addedFileCol bind:addedFileScale bind:addedfiles bind:addedFile on:addfile="{(e)=>plotData({e:e.detail.event, filetype:"addfile"})}" />

<!-- Layout -->

<Layout bind:preModal {filetype} {id} bind:currentLocation bind:fileChecked bind:toggleBrowser on:tour={init_tour}>
    <div class="buttonSlot" slot="buttonContainer">
        <InitFunctionRow {removeExtraFile} {felixPlotCheckboxes} {opofiles} {felixfiles} {normMethod} bind:preModal bind:graphPlotted bind:show_theoryplot/>
        <OPORow {removeExtraFile} bind:OPOLocation bind:OPOfilesChecked bind:opofiles bind:preModal bind:graphPlotted />
        <TheoryRow bind:theoryLocation bind:show_theoryplot bind:preModal {normMethod} {currentLocation}/>
        <div style="display:flex;">
            <CustomRadio on:change={replot} bind:selected={felix_normMethod} options={["Log", "Relative", "IntensityPerPhoton"]}/>
        </div>
    </div>
    
    <div class="plotSlot" slot="plotContainer">

        <!-- Get file info functions -->
        <GetFileInfoTable {plotData} />
        
        <!-- Plots container -->
        <div class="felixPlot">
            <div class="animated fadeIn" class:hide={!show_theoryplot} id="exp-theory-plot"></div>
            <div id="bplot"></div>
            <div id="saPlot"></div>
            <div id="avgplot"></div>
            <div class="animated fadeIn" class:hide={!$opoMode} id="opoplot"></div>
            <div class="animated fadeIn" class:hide={!$opoMode} id="opoSA"></div>
            <div class="animated fadeIn" class:hide={!$opoMode} id="opoRelPlot"></div>
        </div>
    
        {#if graphPlotted}
            <div transition:fade>
                <!-- Write function buttons -->
                <WriteFunctionContents on:addfile="{()=>{addFileModal=true}}" on:removefile={removeExtraFile} {output_namelists} bind:writeFileName bind:writeFile bind:overwrite_expfit />

                <!-- Execute function buttons -->
                <ExecuteFunctionContents {addedFileScale} {addedFileCol} {normMethod} {writeFileName} {writeFile} {overwrite_expfit} {fullfiles} bind:preModal />

                <!-- Frequency table list -->
                <FrequencyTable bind:keepTable/>

                <!-- Report -->
                <ReportLayout bind:currentLocation={currentLocation} id={`${filetype}_report`} {includePlotsInReport} {includeTablesInReports} />
            </div>
        
        {/if}
    </div>

</Layout>