<script>
    // IMPORTING Modules
    import {felixIndex, felixPeakTable, felixOutputName, opoMode, dataTable, dataTable_avg} from './normline/functions/svelteWritables';
    import Textfield from '@smui/textfield'
    import Layout, {createToast} from "../components/Layout.svelte"
    import { fade } from 'svelte/transition'
    
    import CustomSwitch from '../components/CustomSwitch.svelte';
    import CustomSelect from '../components/CustomSelect.svelte';
    import CustomIconSwitch from '../components/CustomIconSwitch.svelte';
    import CustomRadio from '../components/CustomRadio.svelte';
    import ReportLayout from '../components/ReportLayout.svelte';

    import {onMount, tick} from "svelte"

    import {Icon} from '@smui/icon-button'
    
    import Table from '../components/Table.svelte'

    // import FelixPlotting from './normline/modals/FelixPlotting.svelte';
    import AdjustInitialGuess from './normline/modals/AdjustInitialGuess.svelte';
    import AddFilesToPlot from './normline/modals/AddFilesToPlot.svelte';
    import FrequencyTable from './normline/components/FrequencyTable.svelte';

    import InitFunctionRow from './normline/widgets/preprocessing/InitFunctionRow.svelte';
    import OPORow from './normline/widgets/preprocessing/OPORow.svelte';
    import TheoryRow from './normline/widgets/preprocessing/TheoryRow.svelte';
    
    import {init_tour_normline} from './normline/initTour';

    import {NGauss_fit_func} from './normline/functions/NGauss_fit';
    import {find_peaks_func} from './normline/functions/find_peaks';
    import {felix_func} from './normline/functions/felix';
    import {opofile_func} from './normline/functions/opofile';
    import {theory_func} from './normline/functions/theory';
    import {exp_fit_func} from './normline/functions/exp_fit';

    import {get_err_func} from './normline/functions/get_err';
   ///////////////////////////////////////////////////////////////////////


    
    const filetype="felix", id="Normline"

    let fileChecked=[], delta=1, toggleRow=false, toggleBrowser = false;
    let currentLocation = localStorage[`${filetype}_location`] || ""
   
    $: felixfiles = fileChecked.map(file=>path.resolve(currentLocation, file))
    $: console.log(`${filetype} currentlocation: \n${currentLocation}`)
    ///////////////////////////////////////////////////////////////////////

    // Theory file
    let sigma = 20, scale=1, show_theoryplot = false
    let theoryLocation = localStorage["theoryLocation"] || currentLocation

    let theoryfiles;

    ///////////////////////////////////////////////////////////////////////
    
    let openShell = false;
    $: console.log("Open Shell: ", filetype, openShell)

    let felix_normMethod = "Relative", normMethod_datas = {}, NGauss_fit_args = {}
    
    let graphPlotted = false, overwrite_expfit = false, writeFile = false

    let line = [], annotations = [], plot_trace_added = 0, line_index_count = 0

    $: console.log("Trace length: ", plot_trace_added)

    let OPOfilesChecked = []
    $: plottedFiles = $opoMode ? OPOfilesChecked.map(file=>file.split(".")[0]) || [] : fileChecked.map(file=>file.split(".")[0]) || []

    $: output_namelists = ["averaged", ...plottedFiles, ...addedfiles.map(file=>path.basename(file)).map(file=>file.split(".")[0])]

    // let output_name = "averaged"
    let writeFileName = ""
    
    let annotation_color = "black"
    let boxSelected_peakfinder = true

    let keepTable = true;


    //////// OPO Plot ///////////
    window.getID = () => Math.random().toString(32).substring(2)

    window.annotation = []

    let plotly_event_created = false, plotly_event_created_opo = false

    const replot = () => {
        if (graphPlotted) {

            let {data, layout} = normMethod_datas[normMethod]
            Plotly.react("avgplot",data, layout, { editable: true })
            line = annotations = lineData_list = [], plot_trace_added = 0
        }
    }

    function plotData({e=null, filetype="felix", general=null, tkplot="run"}={}){
        let expfit_args = [], double_fit_args = [], find_peaks_args = {}

        switch (filetype) {

            case "felix":
                removeExtraFile()
                graphPlotted = false, $felixOutputName = "averaged", window.annotation = [], $felixPeakTable = []
                
                if(felixfiles.length<1) return createToast("No files selected", "danger")
                break;
            
            case "baseline":
                if ($opoMode) {if(opofiles.length<1) return createToast("No OPO files selected", "danger")}
                else {if(felixfiles.length<1) return createToast("No FELIX files selected", "danger")}
                break;

            case "exp_fit":
                if ($felixIndex.length<2) { return createToast("Range not found!!. Select a range using Box-select", "danger") }

                expfit_args = { addedFileScale, addedFileCol, output_name:$felixOutputName, overwrite_expfit, writeFile, writeFileName, normMethod, index:$felixIndex, fullfiles, location }

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

                NGauss_fit_args = {...NGauss_fit_args, location, addedFileScale, addedFileCol, overwrite_expfit, writeFile, writeFileName, output_name:$felixOutputName, fullfiles, normMethod}
                break;
            
            case "find_peaks":
                
                $felixPeakTable = []

                if ($felixIndex.length<2 && boxSelected_peakfinder) { return createToast("Box selection is turned ON so please select a wn. range to fit", "danger") }
                
                let selectedIndex = boxSelected_peakfinder ? $felixIndex : [0, 0]


                find_peaks_args = { addedFileScale, addedFileCol, output_name:$felixOutputName, normMethod, peak_prominence, peak_width, peak_height, selectedIndex, fullfiles, location }

                break;

            case "opofile":
                removeExtraFile()
                if(opofiles.length<1) return createToast("No files selected", "danger")

                $opoMode = true, window.annotation = []
                break;

            case "get_err":
                if (lineData_list.length<2) return createToast("Not sufficient lines collected!", "danger")
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
            get_err: {pyfile:"weighted_error.py" , args:lineData_list},
            double_peak: {pyfile:"double_gaussian.py" , args:double_fit_args},
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
                        
                        line = [], annotations = [], lineData_list = [], plot_trace_added = 0
                        show_theoryplot = false

                        if (!keepTable) {$dataTable = $dataTable_avg = []}
                        
                        plotly_event_created = felix_func({normMethod, dataFromPython, delta, plotly_event_created})
                        
                        createToast("Graph Plotted", "success")
                        graphPlotted = true
                    } else if (filetype == "opofile") {

                        plotly_event_created_opo = opofile_func({dataFromPython, plotly_event_created_opo})
                        createToast("Graph Plotted", "success")

                        graphPlotted = true, $opoMode = true

                    } else if (filetype == "theory") {

                        theory_func({dataFromPython, normMethod})
                        createToast("Graph Plotted", "success")
                        show_theoryplot = true

                    } else if (filetype == "exp_fit") {

                        [line, annotations, plot_trace_added, line_index_count, collectData, lineData_list] = exp_fit_func({dataFromPython, graphDiv, output_name:$felixOutputName, line, annotations, plot_trace_added, line_index_count, collectData, lineData_list})

                        createToast("Line fitted with gaussian function", "success")

                    } else if (filetype == "get_err") {

                        get_err_func({dataFromPython})
                        createToast("Weighted fit. done", "success")

                    } else if (filetype == "find_peaks") {

                        annotation_color = find_peaks_func({graphDiv, dataFromPython, annotation_color, Ngauss_sigma})
                        console.log(`felixPeakTable: ${$felixPeakTable}`)
                        createToast("Peaks found", "success")
                    } else if (filetype == "NGauss_fit") {

                        line_index_count = NGauss_fit_func({graphDiv, dataFromPython, output_name:$felixOutputName, line_index_count})
                        console.log("Line fitted")
                        createToast(`Line fitted with ${dataFromPython["fitted_parameter"].length} gaussian function`, "success")
                        plot_trace_added++

                    } else if (filetype == "addfile") {
                        addFileModal = false
                        Plotly.addTraces(graphDiv, dataFromPython)
                        
                        extrafileAdded += addedfiles.length

                    } else if (filetype == "get_details") {
                        showfile_details = true

                        filedetails = dataFromPython.files.map(data => {
                            let {filename, trap, res, b0, range} = data
                            let [min, max] = range
                            return {filename, min, max, trap, b0, res, precursor:"", ie:"", temp:"", id:getID()}
                        })
                       
                    }

                } catch (err) { preModal.modalContent = err.stack; preModal.open = true }
            }
            console.log("Process closed")
            target.classList.toggle("is-loading")
            
        })
    }

    const clearAllPeak = () => {


        if (plot_trace_added === 0) {return createToast("No fitted lines found", "danger")}

        console.log("Removing all found peak values")
        
        annotations = $felixIndex = line = lineData_list = []

        Plotly.relayout(graphDiv, { annotations: [], shapes: [] })
        
        for (let i=0; i<plot_trace_added; i++) {Plotly.deleteTraces(graphDiv, [-1])}
        
        plot_trace_added = 0
    }

    const clearLastPeak = () => {
        
        if (plot_trace_added === 0) {return createToast("No fitted lines found", "danger")}

        plotData({filetype:"general", general:{args:[$felixOutputName, location], pyfile:"delete_fileLines.py"}})
        $dataTable = _.dropRight($dataTable, 1)
        line = _.dropRight(line, 2)
        annotations = _.dropRight(annotations, 1)
        lineData_list = _.dropRight(lineData_list, 1)
        Plotly.relayout(graphDiv, { annotations: annotations, shapes: line })

        Plotly.deleteTraces(graphDiv, [-1])
        console.log("Last fitted peak removed")
        plot_trace_added--
    }
    
    let collectData = true, lineData_list = []

    let toggleFindPeaksRow = false
    let peak_height = 1, peak_width = 3, peak_prominence = 0;
    
    let style = "width:7em; height:3.5em; margin-right:0.5em";
    // OPO
    let OPOLocation = localStorage["opoLocation"] || currentLocation
    let opofiles = []
    
    $: normMethod = $opoMode ? "Log" : felix_normMethod
    $: location = $opoMode ? OPOLocation : currentLocation

    $: graphDiv = $opoMode ? "opoRelPlot" : "avgplot"
    
    
    let deltaOPO = 0.3, calibValue = 9394.356278462961.toFixed(4), calibFile = ""
    
    
    $: $opoMode ? createToast("OPO MODE") : createToast("FELIX MODE")
    
    
    $: Ngauss_sigma = $opoMode ? 2 : 5
    let modalActivate = false, addFileModal=false, addedFileCol="0, 1", addedFile={}, addedFileScale=1, addedfiles = [], extrafileAdded=0
    
    $: console.log(`Extrafile added: ${extrafileAdded}`)
   
    function removeExtraFile() {

        for(let i=0; i<extrafileAdded; i++) {
            try {Plotly.deleteTraces(graphDiv, [-1])}

            catch (err) {console.log("The plot is empty")}
        }
        extrafileAdded = 0, addedfiles = []
    }

    let fullfiles = []
    $: $opoMode ? fullfiles = [...opofiles, ...addedfiles, path.resolve(currentLocation, "averaged.felix")] : fullfiles = [...felixfiles, ...addedfiles, path.resolve(currentLocation, "averaged.felix")]

    function adjustPeak({closeMainModal=true}={}) {

        $felixPeakTable = _.filter($felixPeakTable, (tb)=>tb.sig != 0);
        
        $felixPeakTable = _.sortBy($felixPeakTable, [(o)=>o["freq"]])

        let temp_annotate = {xref:"x", y:"y", "showarrow":true,  "arrowhead":2, "ax":-25, "ay":-40, font:{color:annotation_color}, arrowcolor:annotation_color}
        
        window.annotation = []

        $felixPeakTable.forEach((f)=>{
            let _annotate = {x:f.freq, y:f.amp, text:`(${f.freq.toFixed(2)}, ${f.amp.toFixed(2)})`}
            window.annotation = [...window.annotation, {...temp_annotate, ..._annotate} ]
        })

        if(closeMainModal) {
            modalActivate = false, createToast("Initial guess adjusted for full spectrum fitting")
        }

        Plotly.relayout(graphDiv, { annotations:window.annotation })
    }
    
    let showfile_details = false, filedetails = [];

    
    function savefile({file={}, name=""}={}) {
        let filename = path.join(location, `${name}.json`)
        fs.writeFile(filename, JSON.stringify({file}), 'utf8', function (err) {

            if (err) {
                console.log("An error occured while writing to File.");
                return createToast("An error occured while writing to File.", "danger")
            }
            return createToast(`${name}.json has been saved.`, "success");
        });
    }

    function loadfile({name=""}={}) {
        let filename = path.join(location, `${name}.json`)
        if(!fs.existsSync(filename)) {return createToast(`${name}.json doesn't exist in DATA dir.`, "danger")}
        let loadedfile = JSON.parse(fs.readFileSync(filename)).file
        if (name === "filedetails") {filedetails = _.uniqBy([...loadedfile, ...filedetails], "filename")}
        else if (name === "peakTable") {$felixPeakTable = _.uniqBy([...loadedfile, ...$felixPeakTable], "freq"); adjustPeak()}
        return createToast(`${name}.json has been loaded.`, "success");
    }
    
    let savePeakfilename = "peakTable"

    const init_tour = async () => {
        if (!toggleBrowser) {toggleBrowser = true; await sleep(600)} // Filebrowser toggling and its animation time to appear
        await tick() // For all the reactive components to render
        init_tour_normline({filetype})

    }

    // let felixplot_modal = false

    const includePlotsInReport = [
        {id: "bplot", include:true, label:"Baseline"}, {id:"saPlot", include:false, label:"SA-Pow"}, 
        {id:"avgplot", include:false, label:"Normalised Spectrum"}, {id:"exp-theory-plot", include:false, label:"Exp-Theory plot"}, 
        {id:"opoplot", include:false, label:"OPO: Baseline"}, {id:"opoSA", include:false, label:"OPO: SA-pow"}, 
        {id:"opoRelPlot", include:false, label:"OPO: Normalised Spectrum"}
    ]

    const includeTablesInReports = [
        {id:"felixTable", include:true, label:"Freq. table"}, {id:"felix_filedetails_table", include:false, label:"File info table"}
    ]

    $: datlocation = path.resolve(location, "../EXPORT")
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

</script>

<style>
    .hide {display: none;}
    .active {display: block; }
    .felixPlot > div {margin-bottom: 1em;}
    .plotSlot > div { width: calc(100% - 1em); margin-top: 1em; }
</style>

<!-- Modals -->
<AdjustInitialGuess bind:active={modalActivate} on:save={adjustPeak}/>
<AddFilesToPlot bind:active={addFileModal} bind:addedFileCol bind:addedFileScale bind:addedfiles bind:addedFile on:addfile="{(e)=>plotData({e:e.detail.event, filetype:"addfile"})}" />


<!-- Layout -->
<Layout bind:preModal {filetype} {id} bind:currentLocation bind:fileChecked bind:toggleBrowser on:tour={init_tour}>

    <div class="buttonSlot" slot="buttonContainer">

        <InitFunctionRow {plotData} bind:delta bind:openShell {felixPlotCheckboxes} bind:toggleRow/>
        <OPORow {plotData} bind:deltaOPO bind:calibValue bind:calibFile bind:OPOLocation bind:OPOfilesChecked bind:opofiles />
        <TheoryRow {plotData} bind:toggleRow bind:theoryLocation bind:sigma bind:scale bind:theoryfiles/>


        <div style="display:flex;">
            <CustomRadio on:change={replot} bind:selected={felix_normMethod} options={["Log", "Relative", "IntensityPerPhoton"]}/>
        </div>

        
    </div>
    
    <div class="plotSlot" slot="plotContainer">

        <!-- Get file info functions -->
        <div class=""> 
           <div style="display:flex;">
                <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"get_details"})}">Get details</button>
                <CustomIconSwitch bind:toggler={showfile_details} icons={["arrow_drop_down", "arrow_drop_up"]}/>
                <button class="button is-link" on:click="{()=>savefile({file:filedetails, name:"filedetails"})}">Save</button>
                <button class="button is-link" on:click="{()=>loadfile({name:"filedetails"})}">Load</button>
           </div>
            
            {#if showfile_details}
                <Table head={["Filename", "min(cm-1)", "max(cm-1)", "Trap(s)", "B0(ms)", "Res.(V)", "IE(eV)", "Temp(K)","Precursor", ]} bind:rows={filedetails} keys={["filename", "min", "max", "trap", "b0", "res", "ie","temp", "precursor"]} tableid="felix_filedetails_table"/>
            {/if}
        </div>

        
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
                <div class="content" >


                    <CustomSelect bind:picked={$felixOutputName} label="Output filename" options={output_namelists}/>
                    <Textfield style="width:7em; margin:0 0.5em;" bind:value={writeFileName} label="writeFileName"/>

                    <CustomSwitch style="margin: 0 1em;" bind:selected={writeFile} label="Write"/>
                    <CustomSwitch style="margin: 0 1em;" bind:selected={overwrite_expfit} label="Overwrite"/>
                    <CustomSwitch style="margin: 0 1em;" bind:selected={collectData} label="Collect"/>
                    <button class="button is-link" on:click="{()=>{addFileModal=true}}">Add files</button>
                    <button class="button is-link" on:click={removeExtraFile}>Remove files</button>
                </div>

                <!-- Execute function buttons -->
                <div class="content">
                    <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"exp_fit"})}">Exp Fit.</button>
                    <button class="button is-link" on:click="{()=>toggleFindPeaksRow = !toggleFindPeaksRow}">Fit NGauss.</button>
                    <button class="button is-warning" on:click={clearLastPeak}>Clear Last</button>
                    <button class="button is-danger" on:click={clearAllPeak}>Clear All</button>
                    <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"get_err"})}">Weighted Mean</button>
                    <button class="button is-warning" on:click="{()=>{lineData_list = []; createToast("Line collection restted", "warning")}}">Reset</button>
                
                </div>

                <!-- Fit peaks functions -->
                <div class="content animated fadeIn hide" class:active={toggleFindPeaksRow}>

                    <div style="margin:1em 0">
                        <CustomSwitch style="margin: 0 1em;" bind:selected={boxSelected_peakfinder} label="BoxSelected"/>
                        <Textfield type="number" {style} step="0.5" bind:value={peak_prominence} label="Prominance" />
                        <Textfield type="number" {style} step="0.5" bind:value={peak_width} label="Width" />
                        <Textfield type="number" {style} step="0.1" bind:value={peak_height} label="Height" />

                        <Textfield style="width:9em" bind:value={Ngauss_sigma} label="Sigma"/>
                        <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"find_peaks"})}">Get Peaks</button>
                    </div>
                    
                    <div style="display:flex; align-items:center">
                        <Icon class="material-icons" on:click="{()=> modalActivate = true}">settings</Icon>
                        <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"NGauss_fit"})}">Fit</button>

                        <Textfield {style} bind:value={savePeakfilename} label="savefile"/>

                        <button class="button is-link" on:click="{()=>savefile({file:$felixPeakTable, name:savePeakfilename})}">Save peaks</button>
                        <button class="button is-link" on:click="{()=>loadfile({name:savePeakfilename})}">Load peaks</button>
                        <button class="button is-danger" on:click="{()=>{window.annotation=[]; $felixPeakTable=[];NGauss_fit_args={}; window.Plotly.relayout(graphDiv, { annotations: [] }); createToast("Cleared", "warning")}}">Clear</button>
                    </div>

                </div>

                <!-- Frequency table list -->
                <FrequencyTable bind:dataTable_avg={$dataTable_avg} bind:dataTable={$dataTable} bind:keepTable bind:line_index_count bind:lineData_list/>

                <!-- Report -->
                <ReportLayout bind:currentLocation={currentLocation} id={`${filetype}_report`} {includePlotsInReport} {includeTablesInReports} />
            
            </div>
        {/if}
    </div>
</Layout>