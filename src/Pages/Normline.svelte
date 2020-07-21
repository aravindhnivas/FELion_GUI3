
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

    import {NGauss_fit_func} from './normline/functions/NGauss_fit';
    
    import {find_peaks_func} from './normline/functions/find_peaks';
    import {felix_func} from './normline/functions/felix';
    import {opofile_func} from './normline/functions/opofile';
    import {theory_func} from './normline/functions/theory';
    import {exp_fit_func} from './normline/functions/exp_fit';
    import {get_err_func} from './normline/functions/get_err';

    import {get_details_func} from './normline/functions/get_details';
    
    import {savefile, loadfile} from './normline/functions/misc';

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
        
        let expfit_args = [], find_peaks_args = {}
        switch (filetype) {

            case "felix":
                removeExtraFile()
                graphPlotted = false, $felixOutputName = "averaged", $felixPlotAnnotations = [], $felixPeakTable = []
                
                if(felixfiles.length<1) return createToast("No files selected", "danger")
                break;
            
            case "baseline":
                if ($opoMode) {if(opofiles.length<1) return createToast("No OPO files selected", "danger")}
                else {if(felixfiles.length<1) return createToast("No FELIX files selected", "danger")}
                break;

            case "exp_fit":
                if ($felixIndex.length<2) { return createToast("Range not found!!. Select a range using Box-select", "danger") }

                expfit_args = { addedFileScale, addedFileCol, output_name:$felixOutputName, overwrite_expfit, writeFile, writeFileName, normMethod, index:$felixIndex, fullfiles, location:$felixopoLocation }

                break;

            case "NGauss_fit":

                if (boxSelected_peakfinder) {
                    if ($felixIndex.length<2) { return createToast("Box selection is turned ON so please select a wn. range to fit", "danger") }
                    NGauss_fit_args.index = $felixIndex

                } else {delete NGauss_fit_args.index}


                
                if ($felixPeakTable.length === 0) {return createToast("No arguments initialised yet.", "danger") }
                
                NGauss_fit_args.fitNGauss_arguments = {}
                $felixPeakTable = _.sortBy($felixPeakTable, [(o)=>o["freq"]])

                $felixPeakTable.forEach((f, index)=>{
                    NGauss_fit_args.fitNGauss_arguments[`cen${index}`] = f.freq
                    NGauss_fit_args.fitNGauss_arguments[`A${index}`] = f.amp

                    NGauss_fit_args.fitNGauss_arguments[`sigma${index}`] = f.sig
                })

                NGauss_fit_args = {...NGauss_fit_args, location:$felixopoLocation, addedFileScale, addedFileCol, overwrite_expfit, writeFile, writeFileName, output_name:$felixOutputName, fullfiles, normMethod}
                break;
            
            case "find_peaks":
                
                $felixPeakTable = []

                if ($felixIndex.length<2 && boxSelected_peakfinder) { return createToast("Box selection is turned ON so please select a wn. range to fit", "danger") }
                
                let selectedIndex = boxSelected_peakfinder ? $felixIndex : [0, 0]


                find_peaks_args = { addedFileScale, addedFileCol, output_name:$felixOutputName, normMethod, peak_prominence, peak_width, peak_height, selectedIndex, fullfiles, location:$felixopoLocation }

                break;

            case "opofile":
                removeExtraFile()
                if(opofiles.length<1) return createToast("No files selected", "danger")

                $opoMode = true, $felixPlotAnnotations = []
                break;

            case "get_err":
                if ($expfittedLinesCollectedData.length<2) return createToast("Not sufficient lines collected!", "danger")
                break;

            case "theory":
                if(theoryfiles.length < 1) return createToast("No files selected", "danger")
                break;

            case "addfile":

                if(addedFile.files < 1) return createToast("No files selected", "danger")
                addedFile["col"] = addedFileCol, addedFile["N"] = fileChecked.length + extrafileAdded
                addedFile["scale"] = addedFileScale

                break;

            case "get_details":
                if(felixfiles.length<1) return createToast("No files selected", "danger")
                break;
            default:
                break;
        }

        const pyfileInfo = { general, 
            baseline: {pyfile:"baseline.py", args: $opoMode ? opofiles: felixfiles},
            felix: {pyfile:"normline.py" , args:[...felixfiles, delta]},
            exp_fit: {pyfile:"exp_gauss_fit.py" , args:[JSON.stringify(expfit_args)]},
            opofile: {pyfile:"oposcan.py" , args:[...opofiles, tkplot, deltaOPO, calibValue, calibFile]},
            find_peaks: {pyfile:"fit_all.py" ,  args: [JSON.stringify(find_peaks_args)]},
            theory: {pyfile:"theory.py" , args:[...theoryfiles, normMethod, sigma, scale, currentLocation, tkplot]},

            get_err: {pyfile:"weighted_error.py" , args:$expfittedLinesCollectedData},
            NGauss_fit: {pyfile:"multiGauss.py" , args:[JSON.stringify(NGauss_fit_args)]},
            addfile: {pyfile:"addTrace.py" , args:[JSON.stringify(addedFile)]},
            get_details: {pyfile:"getfile_details.py", args:[JSON.stringify({files:$opoMode?opofiles : felixfiles, normMethod})]}
        }

        const {pyfile, args} = pyfileInfo[filetype]
        console.log(pyfileInfo[filetype])

        if(tkplot === "plot") {filetype = "general"}
        if (filetype == "general") {
            
            console.log("Sending general arguments: ", args)

            let py = spawn(
                localStorage["pythonpath"], [path.join(localStorage["pythonscript"], pyfile), args], 
                { detached: true, stdio: 'pipe', shell: openShell }
            )
            py.on("close", ()=>{ console.log("Closed") })
            py.stderr.on("data", (err)=>{ console.log(`Error Occured: ${err.toString()}`); preModal.modalContent = err.toString(); preModal.open = true })
            py.stdout.on("data", (data)=>{ console.log(`Output from python: ${data.toString()}`)  })

            py.unref()
            py.ref()
            return createToast("Process Started")
        }

        let py;
        try {py = spawn( localStorage["pythonpath"], [path.resolve(localStorage["pythonscript"], pyfile), args] )}
        catch (err) {
            preModal.modalContent = "Error accessing python. Set python location properly in Settings"
            preModal.open = true
            return
        }
        
        let target = e.target
        target.classList.toggle("is-loading")

        createToast("Process Started")
        py.stdout.on("data", data => {

            console.log("Ouput from python")
            let dataReceived = data.toString("utf8")
            console.log(dataReceived)
        })
        let error_occured_py = false;
        py.stderr.on("data", err => {
            preModal.modalContent = err
            preModal.open = true
            error_occured_py = true
        });

        py.on("close", () => {
            if (!error_occured_py) {

                try {
                    let dataFromPython = fs.readFileSync(path.join(localStorage["pythonscript"], "data.json"))
                    window.dataFromPython = dataFromPython = JSON.parse(dataFromPython.toString("utf-8"))
                    console.log(dataFromPython)
                    
                    if (filetype == "felix") {
                        $expfittedLines = [], $felixPlotAnnotations = [], $expfittedLinesCollectedData = [], $fittedTraceCount = 0
                        show_theoryplot = false

                        if (!keepTable) {$dataTable = $dataTable_avg = []}
                        
                        felix_func({normMethod, dataFromPython, delta})
                        
                        createToast("Graph Plotted", "success")
                        graphPlotted = true
                    } else if (filetype == "opofile") {

                        opofile_func({dataFromPython})
                        createToast("Graph Plotted", "success")

                        graphPlotted = true, $opoMode = true

                    } else if (filetype == "theory") {

                        theory_func({dataFromPython, normMethod})
                        createToast("Graph Plotted", "success")
                        show_theoryplot = true

                    } else if (filetype == "exp_fit") {

                        exp_fit_func({dataFromPython})

                        createToast("Line fitted with gaussian function", "success")

                    } else if (filetype == "get_err") {

                        get_err_func({dataFromPython})
                        createToast("Weighted fit. done", "success")

                    } else if (filetype == "find_peaks") {

                        find_peaks_func({dataFromPython})
                        console.log(`felixPeakTable:`, $felixPeakTable)
                        createToast("Peaks found", "success")
                    } else if (filetype == "NGauss_fit") {

                        NGauss_fit_func({dataFromPython})
                        console.log("Line fitted")
                        createToast(`Line fitted with ${dataFromPython["fitted_parameter"].length} gaussian function`, "success")

                    } else if (filetype == "addfile") {
                        addFileModal = false
                        Plotly.addTraces($graphDiv, dataFromPython)
                        extrafileAdded += addedfiles.length
                    } else if (filetype == "get_details") { get_details_func({dataFromPython}) }

                } catch (err) { preModal.modalContent = err.stack; preModal.open = true }
            }
            console.log("Process closed")
            target.classList.toggle("is-loading")
            
        })
    }
    
    let peak_height = 1, peak_width = 3, peak_prominence = 0;
    
    // OPO
    let OPOLocation = localStorage["opoLocation"] || currentLocation

    
    let opofiles = []
    $: normMethod = $opoMode ? "Log" : felix_normMethod
    $: $felixopoLocation = $opoMode ? OPOLocation : currentLocation
    let deltaOPO = 0.3, calibValue = 9394.356278462961.toFixed(4), calibFile = ""

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
        <InitFunctionRow {plotData} bind:delta bind:openShell {felixPlotCheckboxes}/>
        <OPORow {plotData} bind:deltaOPO bind:calibValue bind:calibFile bind:OPOLocation bind:OPOfilesChecked bind:opofiles />
        <TheoryRow {plotData} bind:theoryLocation bind:sigma bind:scale bind:theoryfiles/>
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
                <ExecuteFunctionContents {plotData} bind:boxSelected_peakfinder bind:peak_height bind:peak_width bind:peak_prominence bind:NGauss_fit_args/>

                <!-- Frequency table list -->
                <FrequencyTable bind:keepTable/>

                <!-- Report -->
                <ReportLayout bind:currentLocation={currentLocation} id={`${filetype}_report`} {includePlotsInReport} {includeTablesInReports} />
            </div>

        {/if}

    </div>
    
</Layout>