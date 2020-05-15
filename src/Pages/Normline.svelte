<script>
    // IMPORTING Modules
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text/index'
    import Layout, {createToast, browse} from "../components/Layout.svelte"
    import { fly, fade } from 'svelte/transition'
    import Ripple from '@smui/ripple'

    import {activated, modalContent} from "../components/Modal.svelte"
    
    import {plot, subplot} from "../js/functions.js"
    import { flip } from 'svelte/animate'
    
    import DataTable, {Head, Body, Row, Cell} from '@smui/data-table'
    import CustomCheckbox from '../components/CustomCheckbox.svelte';
    import CustomSwitch from '../components/CustomSwitch.svelte';

    import CustomSelect from '../components/CustomSelect.svelte';

    import CustomIconSwitch from '../components/CustomIconSwitch.svelte';
    import CustomRadio from '../components/CustomRadio.svelte';
    import ReportLayout from '../components/ReportLayout.svelte';
    import QuickView from '../components/QuickView.svelte';
    import FileBrowser from "../components/FileBrowser.svelte"
    import Checkbox from '@smui/checkbox';

    import FormField from '@smui/form-field';

    const {BrowserWindow} = remote
    import {onMount} from "svelte"
    import VirtualList from '@sveltejs/svelte-virtual-list';
    import {Icon} from '@smui/icon-button'
    // import Table from '../components/Table.svelte'
    import Modal1 from '../components/Modal1.svelte'

   ///////////////////////////////////////////////////////////////////////
    
    const filetype="felix", id="Normline"

    let fileChecked=[], delta=1, toggleRow=false;
    let currentLocation = localStorage[`${filetype}_location`] || ""
    $: felixfiles = fileChecked.map(file=>path.resolve(currentLocation, file))
    $: console.log(`${filetype} currentlocation: \n${currentLocation}`)

    ///////////////////////////////////////////////////////////////////////

    // Theory file
    let sigma = 20, scale=1, theoryfilesChecked = [], show_theoryplot = false,  showTheoryFiles = false
    let theoryLocation = localStorage["theoryLocation"] || currentLocation
    $: theoryfiles = theoryfilesChecked.map(file=>path.resolve(theoryLocation, file))

    ///////////////////////////////////////////////////////////////////////
    let openShell = false;
    $: console.log("Open Shell: ", filetype, openShell)

    let normMethod = "Relative", normMethod_datas = {}, NGauss_fit_args = {}
    
    let graphPlotted = false, overwrite_expfit = false, writeFile = false
    let line = [], index = [], annotations = [], plot_trace_added = 0, double_peak_active = false, line_index_count = 0

    $: console.log("Trace length: ", plot_trace_added)
    $: console.log("Double peak active: ", double_peak_active)
    $: output_namelists = ["averaged", ...plottedFiles, ...addedfiles.map(file=>path.basename(file)).map(file=>file.split(".")[0])]

    let output_name = "averaged", writeFileName = ""
    let dataTableHead = ["Filename", "Frequency (cm-1)", "Amplitude", "FWHM", "Sigma"]

    let dataTable = [], dataTable_avg = []

    $: dataTable_weighted_avg = dataTable_avg.filter(file=> file.name == "weighted_mean")

    $: console.log("dataTable", dataTable)
    $: console.log("dataTable_avg", dataTable_avg)

    $: console.log("dataTable_weighted_avg", dataTable_weighted_avg)

    let annotation_color = "black"
    let boxSelected_peakfinder = true
    let show_dataTable_only_averaged = false, keepTable = true, show_dataTable_only_weighted_averaged=false

    //////// OPO Plot ///////////
    window.getID = () => Math.random().toString(32).substring(2)
    let opoPlotted = false, onlyFinalSpectrum = false, peakTable = []
    window.annotation = []

    let plotly_event_created = plotly_event_created_opo = false

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
                graphPlotted = false, output_name = "averaged", window.annotation = [], peakTable = removedTable = []
                
                if(felixfiles.length<1) return createToast("No files selected", "danger")
                break;
            
            case "baseline":

                if (OPORow) {if(opofiles.length<1) return createToast("No OPO files selected", "danger")}
                else {if(felixfiles.length<1) return createToast("No FELIX files selected", "danger")}
                break;

            case "exp_fit":
                if (index.length<2) { return createToast("Range not found!!. Select a range using Box-select", "danger") }

                expfit_args = { addedFileScale, addedFileCol, output_name, overwrite_expfit, writeFile, writeFileName, normMethod: opoExpFit ? "Log" : normMethod, index, fullfiles, location: opoExpFit ? OPOLocation : currentLocation }
                break;

            case "double_peak":
                double_fit_args = opoExpFit ? [amp1, amp2, cen1, cen2, sig1, sig2, ...opofiles, overwrite_expfit, output_name, "Log", OPOLocation, ...index ]
                    : [amp1, amp2, cen1, cen2, sig1, sig2, ...felixfiles, overwrite_expfit, output_name, normMethod, currentLocation, ...index ]
                break;

            case "NGauss_fit":
                NGauss_fit_args = {...NGauss_fit_args, location: opoExpFit ? OPOLocation : currentLocation, addedFileScale, addedFileCol, overwrite_expfit, writeFile, writeFileName, output_name, fullfiles, normMethod: opoExpFit ? "Log" : normMethod, output_name}
                break;
            
            case "find_peaks":
                
                peakTable = removedTable = []

                if (index.length<2 && boxSelected_peakfinder) { return createToast("Range not found!!. Select a range using Box-select", "danger") }
                NGauss_fit_args = {fitNGauss_arguments:{}}
                
                let selectedIndex = boxSelected_peakfinder ? index : [0, 0]


                find_peaks_args = { addedFileScale, addedFileCol, output_name, normMethod: opoExpFit ? "Log" : normMethod, peak_prominence, peak_width, peak_height, selectedIndex, fullfiles, location: opoExpFit ? OPOLocation : currentLocation }

                break;

            case "opofile":
                removeExtraFile()
                if(opofiles.length<1) return createToast("No files selected", "danger")
                opoPlotted = true, window.annotation = []
                break;

            case "get_err":
                if (double_peak_active) { lineData_list = err_data1_plot ? weighted_error[0] : weighted_error[1] }
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

            default:
                break;
        }

        const pyfileInfo = { general, 
            baseline: {pyfile:"baseline.py", args: OPORow ? opofiles: felixfiles},
            felix: {pyfile:"normline.py" , args:[...felixfiles, delta]},
            exp_fit: {pyfile:"exp_gauss_fit.py" , args:[JSON.stringify(expfit_args)]},
            opofile: {pyfile:"oposcan.py" , args:[...opofiles, tkplot, delta_OPO, calibValue, calibFile]},
            find_peaks: {pyfile:"fit_all.py" ,  args: [JSON.stringify(find_peaks_args)]},
            theory: {pyfile:"theory.py" , args:[...theoryfiles, normMethod, sigma, scale, currentLocation, tkplot]},
            get_err: {pyfile:"weighted_error.py" , args:lineData_list},
            double_peak: {pyfile:"double_gaussian.py" , args:double_fit_args},
            NGauss_fit: {pyfile:"multiGauss.py" , args:[JSON.stringify(NGauss_fit_args)]},
            addfile: {pyfile:"addTrace.py" , args:[JSON.stringify(addedFile)]}

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
            py.stderr.on("data", (err)=>{ console.log(`Error Occured: ${err.toString()}`); $modalContent = err.toString(); $activated = true })
            py.stdout.on("data", (data)=>{ console.log(`Output from python: ${data.toString()}`)  })

            py.unref()
            py.ref()
            return createToast("Process Started")
        }

        let py;
        try {py = spawn( localStorage["pythonpath"], [path.resolve(localStorage["pythonscript"], pyfile), args] )}
        catch (err) {
            $modalContent = "Error accessing python. Set python location properly in Settings"
            $activated = true
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
            $modalContent = err
            $activated = true
            error_occured_py = true
        });
        py.on("close", () => {

            if (!error_occured_py) {
                try {
                    let dataFromPython = fs.readFileSync(path.join(localStorage["pythonscript"], "data.json"))
                    window.dataFromPython = dataFromPython = JSON.parse(dataFromPython.toString("utf-8"))
                    console.log(dataFromPython)
                    
                    if (filetype == "felix") {
                        opoExpFit = false, output_name = "averaged"
                        line = [], index = [], annotations = [], lineData_list = [], plot_trace_added = 0

                        show_theoryplot = false
                        if (!keepTable) {dataTable = []}

                        let avgdataToPlot;
                        let signal_formula;
                        let ylabel;

                        if (normMethod === "Log") {
                            avgdataToPlot = dataFromPython["average"]
                            signal_formula = "Signal = -ln(C/B)/Power(in J)"
                            ylabel = "Normalised Intensity per J"
                        } else if (normMethod == "Relative") {

                            avgdataToPlot = dataFromPython["average_rel"]

                            signal_formula = "Signal = (1-C/B)*100"
                            ylabel = "Relative Depletion (%)"

                        } else if (normMethod == "IntensityPerPhoton") {

                            avgdataToPlot = dataFromPython["average_per_photon"]

                            signal_formula = "Signal = -ln(C/B)/#Photons"
                            ylabel = "Normalised Intensity per photon"
                        }
                        const get_data = (data) => {
                            let dataPlot = [];
                            for (let x in data) { dataPlot.push(data[x]) }
                            return dataPlot
                        }
                        let signal = {
                            "rel": "Signal = (1-C/B)*100",
                            "log": "Signal = -ln(C/B)/Power(in J)",
                            "hv": "Signal = -ln(C/B)/#Photons"
                        }
                        const set_title = (method) => `Normalised and Averaged Spectrum (delta=${delta})<br>${signal[method]}; {C=Measured Count, B=Baseline Count}`

                        normMethod_datas = {
                            "Relative": {
                                "data": get_data(dataFromPython["average_rel"]),
                                "layout": {
                                    "title": set_title("rel"),
                                    "yaxis": { "title": "Relative Depletion (%)" },
                                    "xaxis": { "title": "Calibrated Wavelength (cm-1)" }
                                }
                            },
                            "Log": {
                                "data": get_data(dataFromPython["average"]),
                                "layout": {
                                    "title": set_title("log"),
                                    "yaxis": { "title": "Normalised Intensity per J" },
                                    "xaxis": { "title": "Calibrated Wavelength (cm-1)" }
                                }
                            },
                            "IntensityPerPhoton": {
                                "data": get_data(dataFromPython["average_per_photon"]),
                                "layout": {
                                    "title": set_title("hv"),
                                    "yaxis": { "title": "Normalised Intensity per photon" },
                                    "xaxis": { "title": "Calibrated Wavelength (cm-1)" }
                                }
                            },

                        }

                        plot(
                            "Baseline Corrected",
                            "Wavelength (cm-1)",
                            "Counts",
                            dataFromPython["base"],
                            "bplot"
                        );

                        plot(
                            `Normalised and Averaged Spectrum (delta=${delta})<br>${signal_formula}; {C=Measured Count, B=Baseline Count}`,
                            "Calibrated Wavelength (cm-1)",
                            ylabel,
                            avgdataToPlot,
                            "avgplot"
                        );

                        subplot(
                            "Spectrum and Power Analyser",
                            "Wavelength set (cm-1)",
                            "SA (cm-1)",
                            dataFromPython["SA"],
                            "saPlot",
                            "Wavelength (cm-1)",
                            `Total Power (mJ)`,
                            dataFromPython["pow"]
                        );

                        let avgplot = document.getElementById("avgplot")
                        if (!plotly_event_created) {

                            console.log("Creating plotly graph events")
                            avgplot.on("plotly_selected", (data) => {
                                if (!data) console.log("No data available to fit")
                                else {

                                    console.log(data)
                                    opoExpFit = false
                                    let { range } = data
                                    output_name = data.points[0].data.name.split(".")[0]
                                    index = range.x
                                    console.log(`Selected file: ${output_name}`)
                                    console.log(`Index selected: ${index}`)
                                }

                            })
                        
                            avgplot.on('plotly_click', (data)=>{
                                console.log("Graph clicked: ", data)

                                if (data.event.ctrlKey) {
                                    console.log("Data point length: ", data.points.length)
                                    for(let i=0; i<data.points.length; i++){

                                        console.log("Running cycle: ", i)
                                        let d = data.points[i]
                                        let name = d.data.name

                                        if (name.includes(output_name)){

                                            console.log("Filename: ", output_name)

                                            NGauss_fit_args = {fitNGauss_arguments:{}}

                                            let line_color = d.data.line.color
                                            console.log(name)
                                            console.log(d, d.x, d.y)

                                            let [freq, amp] = [parseFloat(d.x.toFixed(2)), parseFloat(d.y.toFixed(2))]
                                            
                                            console.log("Annotation before: ", window.annotation)
                                            window.annotation = [...window.annotation, { text: `(${freq}, ${amp}})`, x: freq, y: amp, font:{color:line_color}, arrowcolor:line_color }]
                                            console.log("Annotation after: ", window.annotation)

                                            Plotly.relayout("avgplot",{annotations: _.uniqBy(window.annotation, 'text')})
                                            
                                            peakTable = [...peakTable, {freq, amp, sig:Ngauss_sigma, id:getID()}]
                                            peakTable = _.uniqBy(peakTable, 'freq')

                                            peakTable.forEach((f, index)=>{
                                                NGauss_fit_args.fitNGauss_arguments[`cen${index}`] = f.freq

                                                NGauss_fit_args.fitNGauss_arguments[`A${index}`] = f.amp
                                                NGauss_fit_args.fitNGauss_arguments[`sigma${index}`] = f.sig
                                            })

                                        }
                                    }
                                    console.log("Running cycle ended")
                                } 
                            })

                            plotly_event_created = true;

                        }
                        console.log("Graph Plotted")
                        createToast("Graph Plotted", "success")
                        graphPlotted = true
                    } else if (filetype == "opofile") {

                        opoExpFit = true, output_name = "averaged"

                        plot("OPO spectrum", "Wavenumber (cm-1)", "Counts", dataFromPython["real"], "opoplot")
                        plot("OPO Calibration", "Set Wavenumber (cm-1)", "Measured Wavenumber (cm-1)", dataFromPython["SA"], "opoSA")

                        plot("OPO spectrum: Depletion (%)", "Wavenumber (cm-1)", "Depletion (%)", dataFromPython["relative"], "opoRelPlot")
                        let opoRelPlot = document.getElementById("opoRelPlot")
                        if(!plotly_event_created_opo){

                            console.log("Creating plotly graph events")

                            opoRelPlot.on("plotly_selected", (data) => {

                                if (!data) console.log("No data available to fit")
                                else {
                                    console.log(data)
                                    opoExpFit = true
                                    let { range } = data
                                    output_name = data.points[0].data.name.split(".")[0]
                                    index = range.x
                                    console.log(`Selected file: ${output_name}`)
                                    console.log(`Index selected: ${index}`)
                                }
                            })

                            plotly_event_created_opo = true
                        }
                        console.log("Graph Plotted")

                        createToast("Graph Plotted", "success")
                        showOPOFiles = false, graphPlotted = true
                        
                    } else if (filetype == "theory") {

                        let ylabel;
                        if (normMethod === "Log") { ylabel = "Normalised Intensity per J" }
                        else if (normMethod === "Relative") { ylabel = "Relative Depletion (%)" }
                        else { ylabel = "Normalised Intensity per Photon" }

                        let theoryData = [];
                        for (let x in dataFromPython["line_simulation"]) { theoryData.push(dataFromPython["line_simulation"][x]) }

                        plot(
                            "Experimental vs Theory",
                            "Calibrated Wavelength (cm-1)",
                            ylabel, [dataFromPython["averaged"], ...theoryData],
                            "exp-theory-plot"
                        )


                        console.log("Graph Plotted")
                        createToast("Graph Plotted", "success")
                        show_theoryplot = true, showTheoryFiles = false

                    } else if (filetype == "exp_fit") {

                        double_peak_active = false
                        Plotly.addTraces(graphDiv, dataFromPython["fit"])
                        line = [...line, ...dataFromPython["line"]]
                        Plotly.relayout(graphDiv, { shapes: line })
                        annotations = [...annotations, dataFromPython["annotations"]]
                        Plotly.relayout(graphDiv, { annotations: annotations })
                        
                        plot_trace_added++
                        let [freq, amp, fwhm, sig] = dataFromPython["table"].split(", ")
                        let color = "#fafafa";
                        if (output_name === "averaged") {
                            color = "#836ac05c"
                            dataTable_avg = [...dataTable_avg, {name: `Line #${line_index_count}`, id:getID(), freq, amp, fwhm, sig, color}]
                            dataTable_avg = _.uniqBy(dataTable_avg, "freq")
                            line_index_count++
                        } else {
                            if (collectData) {
                                console.log("Collecting lines")
                                lineData_list = [...lineData_list, dataFromPython["for_weighted_error"]]
                             }
                        }
                        
                        let newTable = {name: output_name, id:getID(), freq, amp, fwhm, sig, color}
                        dataTable = _.uniqBy([...dataTable, newTable], "freq")
                        console.log("Line fitted")
                        createToast("Line fitted with gaussian function", "success")

                    } else if (filetype == "get_err") {

                        let {freq, amp, fwhm, sig } = dataFromPython
                        
                        let data1 = {name: "unweighted_mean", id:getID(), freq:freq.mean, amp:amp.mean, fwhm:fwhm.mean, sig:sig.mean, color:"#f14668"}
                        let data2 = {name: "weighted_mean", id:getID(), freq:freq.wmean, amp:amp.wmean, fwhm:fwhm.wmean, sig:sig.wmean, color:"#2098d1"}
                        dataTable = [...dataTable, data1, data2]
                        dataTable_avg = [...dataTable_avg, data1, data2]

                        if (double_peak_active) {
                            err_data1_plot ? weighted_error[0] = [] : weighted_error[1] = []
                            err_data1_plot = false
                        } else {  lineData_list = [] }

                        console.log("Weighted fit.")
                        createToast("Weighted fit. done", "success")

                    } else if (filetype == "double_peak") {
                        double_peak_active = true
                        console.log("Double peak calculation")
                        Plotly.addTraces(graphDiv, dataFromPython["peak"])
                        plot_trace_added++

                        annotations = [...annotations, ...dataFromPython["annotations"]]
                        Plotly.relayout(graphDiv, { annotations: annotations })
                        let [freq1, amp1, sig1, fwhm1, freq2, amp2, sig2, fwhm2] = dataFromPython["table"].split(", ")
                        let color = "#fafafa";

                        if (output_name === "averaged") {
                            color = "#452f7da8"
                            
                            let newTable1 = {name: `Line #${line_index_count}`, id:getID(), freq:freq1, amp:amp1, fwhm:fwhm1, sig:sig1, color:color}
                            let newTable2 = {name: `Line #${line_index_count+1}`, id:getID(), freq:freq2, amp:amp2, fwhm:fwhm2, sig:sig2, color:color}
                            
                            dataTable_avg = [...dataTable_avg, newTable1, newTable2]
                            dataTable_avg = _.uniqBy(dataTable_avg, "freq")
                            line_index_count += 2
                            
                        } else {
                            if (collectData) {
                                console.log("Collecting lines")
                                err_data1_plot = true    
                                weighted_error[0] = [...weighted_error[0], dataFromPython["for_weighted_error1"]]
                                weighted_error[1] = [...weighted_error[1], dataFromPython["for_weighted_error2"]]
                             }

                        }

                        let newTable1 = {name: output_name, id:getID(), freq:freq1, amp:amp1, fwhm:fwhm1, sig:sig1, color:color}
                        let newTable2 = {name: output_name, id:getID(), freq:freq2, amp:amp2, fwhm:fwhm2, sig:sig2, color:color}
                        dataTable = _.uniqBy([...dataTable, newTable1, newTable2], "freq")

                        console.log("Line fitted Line fitted with double gaussian function")
                        createToast("Line fitted with double gaussian function", "success")

                    } else if (filetype == "find_peaks") {

                        Plotly.relayout(graphDiv, { annotations: [] })
                        window.annotation = dataFromPython[2]["annotations"]

                        annotation_color = dataFromPython[2]["annotations"]["arrowcolor"]
                        Plotly.relayout(graphDiv, { annotations: dataFromPython[2]["annotations"] })

                        
                        if (boxSelected_peakfinder) {NGauss_fit_args.index = index}
                        setTimeout(()=> {

                            const [peakX, peakY] = [dataFromPython[0]["data"].x, dataFromPython[0]["data"].y]
                            setTimeout(()=>{[window.peakX, window.peakY] = [peakX, peakY]}, 500)
                            NGauss_fit_args.peakFilename = dataFromPython[3]["filename"]

                            // let color = "#fafafa";
                            for (let index = 0; index < peakX.length; index++) {
                                let [freq, amp, sig] = [peakX[index], peakY[index], Ngauss_sigma]
                                peakTable = [...peakTable, {freq, amp, sig, id:getID()}]
                                NGauss_fit_args.fitNGauss_arguments[`cen${index}`] = peakX[index]
                                NGauss_fit_args.fitNGauss_arguments[`A${index}`] = peakY[index]
                                NGauss_fit_args.fitNGauss_arguments[`sigma${index}`] = Ngauss_sigma
                            }
                            originalTable = peakTable;

                            console.log(`Found peaks:\nX: ${peakX}\nY: ${peakY}`)

                            console.log(`NGauss_fit_args:`, NGauss_fit_args)
                        }, 500)
                        console.log("Peaks found")
                        createToast("Peaks found", "success")
                    } else if (filetype == "NGauss_fit") {

                        Plotly.addTraces(graphDiv, dataFromPython["fitted_data"])
                        let color = "#fafafa";
                        dataFromPython["fitted_parameter"].forEach(data=>{
                            let {freq, amp, fwhm, sig} = data
                            if (output_name === "averaged") {
                                color = "#836ac05c"
                                dataTable_avg = [...dataTable_avg, {name: `Line #${line_index_count}`, id:getID(), freq:freq, amp:amp, fwhm:fwhm, sig:sig, color:color}]
                                dataTable_avg = _.uniqBy(dataTable_avg, "freq")
                                line_index_count++
                            }

                            let newTable = {name: output_name, id:getID(), freq:freq, amp:amp, fwhm:fwhm, sig:sig, color:color}
                            dataTable = _.uniqBy([...dataTable, newTable], "freq")
                        })

                        console.log("Line fitted")
                        createToast(`Line fitted with ${dataFromPython["fitted_parameter"].length} gaussian function`, "success")

                        plot_trace_added++

                    } else if (filetype == "addfile") {
                        addFileModal = false
                        Plotly.addTraces(graphDiv, dataFromPython)
                        extrafileAdded += addedfiles.length
                    }

                } catch (err) { $modalContent = err; $activated = true }
            }
            console.log("Process closed")
            target.classList.toggle("is-loading")
            
        })
    }
    const clearAllPeak = () => {
        if (plot_trace_added === 0) {return createToast("No fitted lines found", "danger")}

        console.log("Removing all found peak values")
        annotations = index = line = lineData_list = []

        Plotly.relayout(graphDiv, { annotations: [], shapes: [] })
        for (let i=0; i<plot_trace_added; i++) {Plotly.deleteTraces(graphDiv, [-1])}
        plot_trace_added = 0
    }

    const clearLastPeak = (e) => {
        
        if (plot_trace_added === 0) {return createToast("No fitted lines found", "danger")}
            
        if (double_peak_active) {
            plotData({filetype:"general", general:{args:[output_name, opoExpFit?OPOLocation:currentLocation], pyfile:"delete_fileLines.py"}})
            plotData({filetype:"general", general:{args:[output_name, opoExpFit?OPOLocation:currentLocation], pyfile:"delete_fileLines.py"}})
            
            dataTable = _.dropRight(dataTable, 2)
            annotations = _.dropRight(annotations, 2)

            weighted_error[0] = _.dropRight(weighted_error[0], 1)
            weighted_error[1] = _.dropRight(weighted_error[1], 1)
            
        } else {
            plotData({filetype:"general", general:{args:[output_name, opoExpFit?OPOLocation:currentLocation], pyfile:"delete_fileLines.py"}})
            dataTable = _.dropRight(dataTable, 1)
            line = _.dropRight(line, 2)
            annotations = _.dropRight(annotations, 1)
            lineData_list = _.dropRight(lineData_list, 1)
        }
        Plotly.relayout(graphDiv, { annotations: annotations, shapes: line })

        Plotly.deleteTraces(graphDiv, [-1])
        console.log("Last fitted peak removed")

        plot_trace_added--
    }
    onMount(()=>{ console.log("Normline mounted") })
    
    let collectData = true, lineData_list = [], toggleDoubleGaussRow = false, weighted_error = [[], []], err_data1_plot = false

    let amp1=0, amp2=0, cen1=0, cen2=0, sig1=5, sig2=5
    let toggleFindPeaksRow = false
    let peak_height = 1, peak_width = 3, peak_prominence = 0;
    
    let style = "width:7em; height:3.5em; margin-right:0.5em";
    // OPO
    let showOPOFiles = false, OPOfilesChecked = [], opoExpFit = false, OPORow = false
    let OPOLocation = localStorage["opoLocation"] || currentLocation

    $: opofiles = OPOfilesChecked.map(file=>path.resolve(OPOLocation, file))
    $: graphDiv = opoExpFit ? "opoRelPlot" : "avgplot"
    $: plottedFiles = opoExpFit ? OPOfilesChecked.map(file=>file.split(".")[0]) || [] : fileChecked.map(file=>file.split(".")[0]) || []
    let delta_OPO = 0.3, calibValue = 9394.356278462961.toFixed(4), calibFile = ""
    
    let OPOcalibFiles = []
    $: if(fs.existsSync(OPOLocation)) {OPOcalibFiles = fs.readdirSync(OPOLocation).filter(file=> file.endsWith(".calibOPO"))}
    $: OPORow ? createToast("OPO MODE") : createToast("FELIX MODE")
    
    $: opoPlotted ? opoExpFit = true : opoExpFit = false
    $: Ngauss_sigma = opoExpFit ? 2 : 5
    let modalActivate = false, addFileModal=false, addedFileCol="0, 1", addedFile={}, addedFileScale=1, addedfiles = [], extrafileAdded=0
    
    $: console.log(`Extrafile added: ${extrafileAdded}`)
    function addFileSelection() {
        
        browse({dir:false}).then(result=>{ 
            if (!result.canceled) {addedfiles = addedFile["files"] = result.filePaths}  
        })

    }
    function removeExtraFile() {

        for(let i=0; i<extrafileAdded; i++) {
            try {Plotly.deleteTraces(graphDiv, [-1])}

            catch (err) {console.log("The plot is empty")}
        }
        extrafileAdded = 0, addedfiles = []
    }

    let fullfiles = [], removedTable = []
    $: opoExpFit ? fullfiles = [...opofiles, ...addedfiles, path.resolve(currentLocation, "averaged.felix")] : fullfiles = [...felixfiles, ...addedfiles, path.resolve(currentLocation, "averaged.felix")]

    function adjustPeak({closeMainModal=true}={}) {

        peakTable = _.filter(peakTable, (tb)=>tb.sig != 0);
        let temp_annotate = {xref:"x", y:"y", "showarrow":true,  "arrowhead":2, "ax":-25, "ay":-40, font:{color:annotation_color}, arrowcolor:annotation_color}
        
        let newAnnotations = []
        NGauss_fit_args.fitNGauss_arguments = {}
        
        peakTable.forEach((f, index)=>{

            NGauss_fit_args.fitNGauss_arguments[`cen${index}`] = f.freq
            NGauss_fit_args.fitNGauss_arguments[`A${index}`] = f.amp
            NGauss_fit_args.fitNGauss_arguments[`sigma${index}`] = f.sig
            let _annotate = {x:f.freq, y:f.amp, text:`(${f.freq.toFixed(2)}, ${f.amp.toFixed(2)})`}
            newAnnotations = [...newAnnotations, {...temp_annotate, ..._annotate} ]
        })
        console.log("Initial gusses changed", NGauss_fit_args.fitNGauss_arguments)
        if(closeMainModal) {
            modalActivate = false, createToast("Initial guess adjusted for full spectrum fitting")
            // removedTable.forEach((f, index)=>{ window.annotation = _.filter(window.annotation, (freq)=>freq.x != f.freq) })
        }
        Plotly.relayout(graphDiv, { annotations:newAnnotations })
        console.log("Fitted arguments", NGauss_fit_args.fitNGauss_arguments)
    }

    let originalTable;
    function rearrangePeakTable(e) {

        peakTable = _.filter(peakTable, (tb)=>tb.id != e.target.id);
        removedTable = _.differenceBy(originalTable, peakTable)
        console.log(originalTable, peakTable, removedTable)
    }

    const editPeakTable = (index) => {
        let freq = parseFloat(document.getElementById(`${index}_tb_freq`).innerHTML)
        let amp = parseFloat(document.getElementById(`${index}_tb_amp`).innerHTML)
        let sig = parseFloat(document.getElementById(`${index}_tb_sig`).innerHTML)
        peakTable[index] = {freq, amp, sig}
        console.log({freq, amp, sig})
    }
    $: console.log(peakTable)
    const focusFreq = (e) => {e.focus()}

    const sortTable = (type) => {
        peakTable = _.sortBy(peakTable, [(o)=>o[type]])
        peakTable = _.reverse(peakTable)
    }
</script>

<style>

    * :global(.button) {margin: 0.4em;}
    * :global(.short-input) { max-width: 7em; margin: 0 1em; }
    * :global(.mdc-text-field--outlined) {height: 2.5em;}
    * :global(.plotSlot) { width: 100%}
    
    * :global(option) { color: black; }
    * :global(.mdc-data-table) {min-width: 30em; background-color: #5b3ea2; max-height: 25em; overflow-y: auto}
    * :global(.mdc-data-table__content ) {background-color: #fafafa;}
    * :global(hr) { width: 90%; margin: 1em 0; }
    * :global(.report) { display: block; margin-bottom: 1em; }
    * :global(table th:not([align])) {text-align: center; padding: 1em;}
    * :global(table td:not([align])) {text-align: center; padding: 1em;}
    * :global(.averagedTable td) { color: white; }

    * :global(.tableContainer) {border: 1px solid #5b3ea2; width:100%; padding-right: 1em;}
    * :global(.tableContainer thead) {background-color: #e1e1e1;}
    .hide {display: none;}
    .active {display: block; }
    .align {display: flex; align-items: center;}
    .felixPlot > div {margin-bottom: 1em;}
    .notification {width: 100%; border: 1px solid;}
    .plotSlot > div { width: calc(100% - 1em); margin-top: 1em; }
    .dataTable { display: flex; justify-content: center; }

    .icon-holder {

        margin: 1em 0;
        width: 2em;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor:pointer;
    }

</style>

<Modal1 bind:active={modalActivate} title="Adjust initial guess" >
    <div slot="content" >
            <div class="icon-holder" use:Ripple={[true, {color: 'primary'}]} ><Icon class="material-icons"  on:click="{(e)=> {peakTable = [...peakTable, {freq:0, amp:0, sig:0, id:window.getID()}]}}">add</Icon></div>

            <!-- Data Table -->
            <div class="mdc-data-table tableContainer" transition:fade>
                <table class="mdc-data-table__table" aria-label="adjustPeaks">

                    <thead>
                        <tr class="mdc-data-table__header-row">
                            <th class="mdc-data-table__header-cell" style="width: 2em;" role="columnheader" scope="col"></th>

                            <th style="cursor: pointer;" class="mdc-data-table__header-cell mdc-data-table__header-cell--numeric" role="columnheader" scope="col" on:click="{()=>sortTable("freq")}">Frequency</th>
                            <th style="cursor: pointer;" class="mdc-data-table__header-cell mdc-data-table__header-cell--numeric" role="columnheader" scope="col" on:click="{()=>sortTable("amp")}">Amplitude</th>
                            <th style="cursor: pointer;" class="mdc-data-table__header-cell mdc-data-table__header-cell--numeric" role="columnheader" scope="col" on:click="{()=>sortTable("sig")}">Sigma</th>
                            
                            <th class="mdc-data-table__header-cell" style="width: 2em;" role="columnheader" scope="col"></th>
                        </tr>
                    </thead>
                    <tbody class="mdc-data-table__content">
                        {#each peakTable as table, index (table.id)}

                            <tr class="mdc-data-table__row" style="background-color: #fafafa;"> 
                                <td class="mdc-data-table__cell" style="width: 2em;" >{index}</td>

                                <td class="mdc-data-table__cell mdc-data-table__cell--numeric"  ><input style="color:black" type="number" step="0.05" bind:value="{table.freq}" use:focusFreq></td>
                                <td  class="mdc-data-table__cell mdc-data-table__cell--numeric" ><input style="color:black" type="number" step="0.05"  bind:value="{table.amp}"></td>
                                <td class="mdc-data-table__cell mdc-data-table__cell--numeric" ><input style="color:black" type="number" step="0.5"  bind:value="{table.sig}"></td>
                                
                                <td class="mdc-data-table__cell" style="background: #f14668; cursor: pointer; width: 2em;" >
                                    <Icon id="{table.id}" class="material-icons" on:click="{(e)=> {rearrangePeakTable(e)}}">close</Icon>
                                </td>
                            </tr>
                        {/each}
                        
                    </tbody>
                </table>
            </div>

    </div>
    <button slot="footerbtn" class="button is-link" on:click={adjustPeak} >Save</button>

</Modal1>



<Modal1 bind:active={addFileModal} title="Add file to plot">

    <div slot="content" >
        <Textfield style="width:7em; margin:0 0.5em;" bind:value={addedFileCol} label="Columns"/>
        <Textfield style="width:7em; margin:0 0.5em;" bind:value={addedFileScale} label="ScaleY"/>
        <button on:click={addFileSelection} class="button is-link">Browse</button>

    </div>
    <button slot="footerbtn" class="button is-link" on:click="{(e)=>{plotData({e:e, filetype:"addfile"})}}" >Add</button>

</Modal1>

<QuickView style="padding:1em;" bind:active={showTheoryFiles} bind:location={theoryLocation}>

    <FileBrowser bind:currentLocation="{theoryLocation}" bind:fileChecked={theoryfilesChecked} filetype=""/>
    <div slot="footer" style="margin:auto">
        <button class="button is-link" on:click="{(e)=>{plotData({e:e, filetype:"theory"}); localStorage["theoryLocation"] = theoryLocation}}">Submit</button>
    </div>
</QuickView>


<QuickView style="padding:1em;" bind:active={showOPOFiles} bind:location={OPOLocation}>
    <FileBrowser bind:currentLocation={OPOLocation} bind:fileChecked={OPOfilesChecked} filetype="ofelix"/>
    <div slot="footer" style="margin:auto">

        <button class="button is-link" on:click="{(e)=>{plotData({e:e, filetype:"opofile"}); localStorage["opoLocation"] = OPOLocation}}">Submit</button>
    </div>
</QuickView>


<Layout {filetype} {id} bind:currentLocation bind:fileChecked >
    <div class="buttonSlot" slot="buttonContainer">

        <div class="align">

            <button class="button is-link" 
                on:click="{(e)=>plotData({e:e, filetype:"baseline", tkplot:"plot"})}">
                Create Baseline</button>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"felix"})}">FELIX Plot</button>

            <Textfield style="width:7em" variant="outlined" bind:value={delta} label="Delta"/>
            <button class="button is-link" 
                on:click="{(e)=>plotData({e:e, filetype:"general", general:{args:[...felixfiles, normMethod, onlyFinalSpectrum], pyfile:"norm_tkplot.py"}})}"> Open in Matplotlib</button>

            <CustomCheckbox bind:selected={onlyFinalSpectrum} label="Only Final spectrum" />
            <CustomIconSwitch bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <button class="button is-link" use:Ripple={[true, {color: 'primary'}]} tabindex="0" on:click="{()=>toggleRow = !toggleRow}">Add Theory</button>
            <button class="button is-link" on:click="{()=>{OPORow = !OPORow}}">OPO</button>
            <CustomIconSwitch bind:toggler={opoPlotted} icons={["keyboard_arrow_up", "keyboard_arrow_down"]}/>

        </div>

        <div class="animated fadeIn hide content" class:active={OPORow} >
            <div class="align">
                <CustomSelect style="width:7em;" bind:picked={calibFile} label="Calib. file" options={["", ...OPOcalibFiles]}/>
                <Textfield on:change="{(e)=>plotData({e:e, filetype:"opofile"})}" style="width:7em; margin:0 0.5em;" bind:value={delta_OPO} label="Delta OPO"/>
                <Textfield on:change="{(e)=>plotData({e:e, filetype:"opofile"})}" style="width:9em" bind:value={calibValue} label="Wn-meter calib."/>
                <button class="button is-link" 
                    on:click="{()=>{showTheoryFiles=false;showOPOFiles = !showOPOFiles; OPOLocation = localStorage["opoLocation"] || currentLocation}}">
                    Browse File</button>
                <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"opofile", tkplot:"plot"})}">Open in Matplotlib</button>
                <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"opofile"})}">Replot</button>
            </div>
        </div>

        <div class="animated fadeIn hide" class:active={toggleRow}>
            <button class="button is-link" 
                on:click="{()=>{showOPOFiles=false;showTheoryFiles = !showTheoryFiles; theoryLocation = localStorage["theoryLocation"] || currentLocation}}">
                Browse File</button>
            <Textfield type="number" style="width:7em; margin-right:0.5em;" variant="outlined" bind:value={sigma} label="Sigma" on:change="{(e)=>plotData({e:e, filetype:"theory"})}"/>
            <Textfield type="number" style="width:7em" variant="outlined" bind:value={scale} label="Scale" on:change="{(e)=>plotData({e:e, filetype:"theory"})}"/>
            <button class="button is-link" 
                on:click="{(e)=>plotData({e:e, filetype:"general", general:{args:[...theoryfiles, normMethod, sigma, scale, theoryLocation, "plot"], pyfile:"theory.py"}})}">Open in Matplotlib</button>
        </div>

        <div on:change={replot}>
            <CustomRadio bind:selected={normMethod} options={["Log", "Relative", "IntensityPerPhoton"]}/>
        </div>
    </div>
    
    <div class="plotSlot" slot="plotContainer">
        <div class="felixPlot">
            <div class="animated fadeIn hide" class:active={show_theoryplot} id="exp-theory-plot"></div>
            
            <div id="bplot"></div>
            
            <div id="saPlot"></div>
            <div id="avgplot"></div>
            <div class="animated fadeIn hide" class:active={opoPlotted} id="opoplot"></div>
            <div class="animated fadeIn hide" class:active={opoPlotted} id="opoSA"></div>
            
            <div class="animated fadeIn hide" class:active={opoPlotted} id="opoRelPlot"></div>
        </div>
        <div class="animated fadeIn hide" class:active={graphPlotted}>
            <div class="content" transition:fade>

                <CustomSwitch style="margin: 0 1em;" bind:selected={opoExpFit} label="OPO"/>

                <CustomSelect bind:picked={output_name} label="Output filename" options={output_namelists}/>
                <Textfield style="width:7em; margin:0 0.5em;" bind:value={writeFileName} label="writeFileName"/>

                <CustomSwitch style="margin: 0 1em;" bind:selected={writeFile} label="Write"/>
                <CustomSwitch style="margin: 0 1em;" bind:selected={overwrite_expfit} label="Overwrite"/>
                <CustomSwitch style="margin: 0 1em;" bind:selected={collectData} label="Collect"/>
                <button class="button is-link" on:click="{()=>{addFileModal=true}}">Add files</button>
                <button class="button is-link" on:click={removeExtraFile}>Remove files</button>

            </div>

            <div class="content">
                <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"exp_fit"})}">Exp Fit.</button>
                <!-- <button class="button is-link" on:click="{(e)=>toggleDoubleGaussRow = !toggleDoubleGaussRow}">Double Gauss.</button> -->
                <button class="button is-link" on:click="{()=>toggleFindPeaksRow = !toggleFindPeaksRow}">Fit NGauss.</button>
                <button class="button is-warning" on:click={clearLastPeak}>Clear Last</button>
                
                <button class="button is-danger" on:click={clearAllPeak}>Clear All</button>
                <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"get_err"})}">Weighted Mean</button>
                <button class="button is-warning" on:click="{(e)=>{lineData_list = []; createToast("Line collection restted", "warning")}}">Reset</button>
            
            </div>

            <div class="content animated fadeIn hide" class:active={toggleFindPeaksRow}>
                <CustomSwitch style="margin: 0 1em;" bind:selected={boxSelected_peakfinder} label="BoxSelected"/>
                
                <Textfield type="number" {style} bind:value={peak_prominence} label="Prominance" />
                <Textfield type="number" {style} bind:value={peak_width} label="Width" />
                <Textfield type="number" {style} bind:value={peak_height} label="Height" />
                
                <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"find_peaks"})}">Get Peaks</button>

                <Textfield style="width:9em" bind:value={Ngauss_sigma} label="Sigma"/>
                <Icon class="material-icons" on:click="{()=> modalActivate = true}">settings</Icon>
                <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"NGauss_fit"})}">Fit</button>
                <button class="button is-danger" on:click="{(e)=>{window.annotation=[]; peakTable=[];NGauss_fit_args={}; window.Plotly.relayout(graphDiv, { annotations: [] })}}">Clear</button>
            </div>

            <div class="content animated fadeIn hide" class:active={toggleDoubleGaussRow}>
                <Textfield type="number" style="width:7em; margin-right:0.5em;" bind:value={amp1} label="Amp1" />
                <Textfield type="number" style="width:7em; margin-right:0.5em;" bind:value={amp2} label="Amp2" />
                <Textfield type="number" style="width:7em; margin-right:0.5em;" bind:value={sig1} label="Sigma1" />
                <Textfield type="number" style="width:7em; margin-right:0.5em;" bind:value={sig2} label="Sigma2" />
                <Textfield type="number" style="width:7em; margin-right:0.5em;" bind:value={cen1} label="Cen1" />
                <Textfield type="number" style="width:7em; margin-right:0.5em;" bind:value={cen2} label="Cen2" />
                <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"double_peak"})}">Submit</button>
            </div>

            <!-- Frequency table list -->
            <div class="content">
                <div class="title notification is-link">Frequency table</div>
                <CustomCheckbox bind:selected={show_dataTable_only_averaged} label="Only Averaged" />
                <CustomCheckbox bind:selected={show_dataTable_only_weighted_averaged} label="Only weighted Averaged" />
                <CustomCheckbox bind:selected={keepTable} label="Keep table" />
                <button class="button is-warning" 
                    on:click="{()=>{dataTable = window._.dropRight(dataTable, 1); lineData_list = window._.dropRight(lineData_list, 1);
                    if(show_dataTable_only_averaged){dataTable_avg = window._.dropRight(dataTable_avg, 3); line_index_count--}}}">Clear Last</button>
                <button class="button is-danger" on:click="{()=>{dataTable=dataTable_avg=[]; line_index_count=0; lineData_list=[]}}">Clear Table</button>

            </div>

            <!-- Data Table -->
            <div class="dataTable" transition:fade>

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
            <ReportLayout bind:currentLocation={currentLocation} id="felixreport" tableID="felixTable"
                plotID={["bplot", "saPlot", "avgplot", "exp-theory-plot", "opoplot", "opoSA", "opoRelPlot"]} includeTable={true}/>

        </div>
    </div>
</Layout>