<script>
    // IMPORTING Modules
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text/index'
    import Layout, {browse, createToast} from "../components/Layout.svelte"
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

   ///////////////////////////////////////////////////////////////////////

    let filetype="felix", id="Normline", fileChecked=[], delta=1, toggleRow=false;
    $: felixfiles = fileChecked.map(file=>path.resolve(currentLocation, file))
    let plottedFiles = []
    let currentLocation = localStorage[`${filetype}_location`] || ""
    
    $: console.log(`${filetype} Update: \n${currentLocation}`)

    ///////////////////////////////////////////////////////////////////////

    // Theory file
    let sigma = 20, scale=1, thoeryfiles = [], show_theoryplot = false,  showTheoryFiles = false,
     theoryLocation = currentLocation
    $: console.log("Theory files: ", thoeryfiles)
    $: console.log("Theory Location", theoryLocation)

    ///////////////////////////////////////////////////////////////////////
    

    let openShell = false;
    $: console.log("Open Shell: ", filetype, openShell)
    let normMethod = "Relative", normMethod_datas = {}
    let graphPlotted = false, overwrite_expfit = false

    let line = [], index = [], annotations = []
    let output_name = "averaged"

    let dataTableHead = ["Filename", "Frequency (cm-1)", "Amplitude", "FWHM", "Sigma"]
    let dataTable = []
    $: dataTable_avg = dataTable.filter(data=>data.name === "averaged")
    $: console.log("dataTable", dataTable)
    $: console.log("dataTable_avg", dataTable_avg)

    let show_dataTable_only_averaged = false, keepTable = true

    //////// OPO Plot ///////////
    let opoPlotted = false;

    ///////////////////////////////////////////////////////////////////////////////////
    
    const replot = () => {
    
        if (graphPlotted) {
            let {data, layout} = normMethod_datas[normMethod]

            Plotly.react("avgplot",data, layout, { editable: true })
        }
    }

    function plotData(event=null, filetype="felix", general=null){

        if (fileChecked.length === 0) {return createToast("No files selected", "danger")}
        let target = event.target
        target.classList.toggle("is-loading")

        if (filetype == "felix") {graphPlotted = false, output_name = "averaged"}
        else if (filetype == "exp_fit") {if (index.length < 2) {
            target.classList.toggle("is-loading")
            return createToast("Range not found!!. Select a range using Box-select", "danger")
        }} else if (filetype == "opofile") {opoPlotted = true}

        let pyfileInfo = {
        
            felix: {pyfile:"normline.py" , args:[...felixfiles, delta]},
            exp_fit: {pyfile:"exp_gauss_fit.py" , args:[...felixfiles, overwrite_expfit, output_name, normMethod, currentLocation, ...index]},
            opofile: {pyfile:"oposcan.py" , args:[...felixfiles, "run"]},
        }

        let {pyfile, args} = pyfileInfo[filetype]
        if (filetype == "general") {
            console.log("Sending general arguments: ", general.args)
            spawn(
                localStorage["pythonpath"],
                ["-i", path.join(localStorage["pythonscript"], general.pyfile), ...general_args],
                { detached: true, stdio: 'ignore', shell: openShell }
            )
            py.unref()
            createToast("General process sent. Expect an response soon...")
            return;
        }

        let py;

        try {py = spawn( localStorage["pythonpath"], [path.resolve(localStorage["pythonscript"], pyfile), args] )}
        catch (err) {
            $modalContent = "Error accessing python. Set python location properly in Settings"
            $activated = true
            target.classList.toggle("is-loading")
            return
        }
        createToast("Process Started")
        py.stdout.on("data", data => {
            console.log("Ouput from python")
            let dataReceived = data.toString("utf8")
            console.log(dataReceived)
        });

        let error_occured_py = false;
        py.stderr.on("data", err => {
            $modalContent = err
            $activated = true
            error_occured_py = true;
        });

        py.on("close", () => {

            if (!error_occured_py) {

                try {
                    let dataFromPython = fs.readFileSync(path.join(localStorage["pythonscript"], "data.json"))
                    dataFromPython = JSON.parse(dataFromPython.toString("utf-8"))

                    console.log(dataFromPython)

                    if (filetype == "felix") {

                        line = []
                        index = []
                        annotations = []
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

                        //Spectrum and Power Analyer
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
                        avgplot.on("plotly_selected", (data) => {
                            if (!data) console.log("No data available to fit")
                            else {
                                console.log(data)

                                let { range } = data
                                output_name = data.points[0].data.name.split(".")[0]
                                index = range.x

                                console.log(`Selected file: ${output_name}`)
                                console.log(`Index selected: ${index}`)
                            }
                        })

                        console.log("Graph Plotted")
                        createToast("Graph Plotted", "success")
                        graphPlotted = true
                        plottedFiles = fileChecked.map(file=>file.split(".")[0])

                    } else if (filetype == "opofile") {
                        plot("OPO spectrum", "Wavenumber (cm-1)", "Counts", dataFromPython["real"], "opoplot");
                        plot("OPO spectrum: Depletion (%)", "Wavenumber (cm-1)", "Depletion (%)", dataFromPython["relative"], "opoRelPlot");
                        
                    } else if (filetype == "theory") {

                        let normethod = this.args[0];
                        let ylabel;
                        if (normethod === "Log") { ylabel = "Normalised Intensity per J" }
                        else if (normethod === "Relative") { ylabel = "Relative Depletion (%)" }
                        else { ylabel = "Normalised Intensity per Photon" }

                        let theoryData = [];
                        for (let x in dataFromPython["line_simulation"]) { theoryData.push(dataFromPython["line_simulation"][x]) }

                        plot(
                            "Experimental vs Theory",
                            "Calibrated Wavelength (cm-1)",
                            ylabel, [dataFromPython["averaged"], ...theoryData],
                            "exp-theory-plot"
                        );
                    } else if (filetype == "exp_fit") {

                        Plotly.addTraces("avgplot", dataFromPython["fit"])
                        line = [...line, ...dataFromPython["line"]]
                        Plotly.relayout("avgplot", { shapes: line })

                        annotations = [...annotations, dataFromPython["annotations"]]
                        Plotly.relayout("avgplot", { annotations: annotations })
                        let [freq, amp, fwhm, sig] = dataFromPython["table"].split(", ")
                        let color;
                        output_name === "averaged" ? color = "#513a8a80" : color = "#fafafa"
                        let id = dataFromPython["freq"];
                        let prevId = ""

                        if (dataTable.length >=1) prevId = _.nth(dataTable, -1).id

                        dataTable = [...dataTable, {name: output_name, id:id, freq:freq, amp:amp, fwhm:fwhm, sig:sig, color:color}]
                        
                        if ( prevId !== "" && prevId == id ) {
                            console.log("Resolving same Id bug for FELIX frequency table", dataTable)
                            dataTable = _.dropRight(dataTable, 1)
                            console.log("Resolved")
                        }
                        

                        console.log("Line fitted")
                        createToast("Line fitted with gaussian function", "success")
                    }
                
                } catch (err) { $modalContent = err; $activated = true }
            }
            console.log("Process closed")
            target.classList.toggle("is-loading")
        })
    }

    const clearAllPeak = () => {
        console.log("Removing all found peak values")

        if (line.length === 0 & annotations.length === 0) {createToast("No fitted lines found", "danger")}
        annotations = []
        index = []
        Plotly.relayout("avgplot", { annotations: [], shapes: [] })

        let plottedFiles_length = line.length / 2
        console.log(`Total files plotted: ${plottedFiles_length}`)
        
        for (let i=0; i<plottedFiles_length; i++) {Plotly.deleteTraces("avgplot", [-1])}
        line = []
        ready_to_fit = false
    }


    const clearLastPeak = () => {

        if (line.length > 0) {
            //   delete_file_line()
            dataTable = _.dropRight(dataTable, 1)

            Plotly.deleteTraces("avgplot", [-1])
            
            console.log("Last fitted peak removed")
            } else {
            if (annotations.length === 0) {createToast("No fitted lines found", "danger")}
            console.log("No line fit is found to remove")
        }
        
        line = _.dropRight(line, 2)
        annotations = _.dropRight(annotations, 1)
        // index = []
        Plotly.relayout("avgplot", { annotations: annotations, shapes: line })
        if (line.length === 0) {ready_to_fit = false}
    }

</script>

<style>

    * :global(.button) {margin: 0.4em;}
    * :global(.short-input) { max-width: 7em; margin: 0 1em; }
    * :global(.mdc-text-field--outlined) {height: 2.5em;}
    * :global(.plotSlot) { width: 100%}

    * :global(option) { color: black; }
    * :global(.mdc-data-table) {min-width: 30em}
    .plotSlot > div { width: calc(100% - 1em); margin-top: 1em; }

    .dataTable {
        display: flex;
        justify-content: center;
    }
    * :global(hr) {
        width: 90%;
        margin: 1em 0;
    }
    * :global(.report) {
        display: block;
        width: 90%;
        margin-bottom: 1em;
    }
    * :global(table th:not([align])) {text-align: center; padding: 1em;}
    * :global(table td:not([align])) {text-align: center; padding: 1em;}
    * :global(#felixTableContainer) {border: 1px solid #5b3ea2;}
    * :global(#felixTableContainer thead) {background-color: #e1e1e1;}

    .active {display: block!important;}
    .hide {display: none;}
    .felixPlot > div {margin-bottom: 1em;}
    .notification {width: 100%; border: 1px solid;}
</style>

<QuickView style="padding:1em;" footer={false} bind:active={showTheoryFiles} title="Browse Theory files">

    <FileBrowser bind:currentLocation={theoryLocation} bind:fileChecked={thoeryfiles} />
</QuickView>

<Layout {filetype} {id} bind:currentLocation bind:fileChecked >

    <div class="buttonSlot" slot="buttonContainer">

        <div class="align" >

            <button class="button is-link">Create Baseline</button>
            <button class="button is-link" on:click="{(e)=>plotData(e, "felix")}">FELIX Plot</button>
            <Textfield style="width:7em" variant="outlined" bind:value={delta} label="Delta" />
            <button class="button is-link">Open in Matplotlib</button>
            <CustomIconSwitch bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <button class="button is-link" use:Ripple={[true, {color: 'primary'}]} tabindex="0" on:click="{()=>toggleRow = !toggleRow}">Add Theory</button>
            <button class="button is-link" on:click="{(e)=>plotData(e, "opofile")}">OPO</button>
            <CustomIconSwitch bind:toggler={opoPlotted} icons={["keyboard_arrow_up", "keyboard_arrow_down"]}/>
            
        </div>

        {#if toggleRow}
            <div class="align" transition:fly="{{ y: -20, duration: 500 }}">
                <button class="button is-link" on:click="{()=>showTheoryFiles = !showTheoryFiles}">Browse File</button>
                <Textfield style="width:7em; margin-right:0.5em;" variant="outlined" bind:value={sigma} label="Sigma" />
                <Textfield style="width:7em" variant="outlined" bind:value={scale} label="Scale" />
                <button class="button is-link">Open in Matplotlib</button>
                <button class="button is-link">Submit</button>
            </div>
        {/if}


        <div class="align" on:change={replot}>
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
            <div class="animated fadeIn hide" class:active={opoPlotted} id="opoRelPlot"></div>
        </div>

        {#if graphPlotted}
            
            <!-- Pos-processing felix data -->
            <div class="content" transition:fade>
                <CustomSelect bind:picked={output_name} label="Output filename" options={["averaged", ...plottedFiles]}/>
                <CustomSwitch style="margin: 0 1em; padding-bottom: 1em;" bind:selected={overwrite_expfit} label="Overwrite"/>
                <button class="button is-link" on:click="{(e)=>plotData(e, "exp_fit")}">Exp Fit.</button>
                <button class="button is-warning" on:click={clearLastPeak}>Clear Last</button>
                <button class="button is-danger" on:click={clearAllPeak}>Clear All</button>
                
            </div>

            <!-- Frequency table list -->
            <div class="align">
                <div class="title notification is-link">Frequency table</div>
                <CustomCheckbox bind:selected={show_dataTable_only_averaged} label="Only Averaged" />
                <CustomCheckbox bind:selected={keepTable} label="Keep table" />
                <button class="button is-warning" on:click="{()=>dataTable = window._.dropRight(dataTable, 1)}">Clear Last</button>
                <button class="button is-danger" on:click="{()=>dataTable = []}">Clear Table</button>
            </div>

            <div class="dataTable" transition:fade>

                <DataTable table$aria-label="{filetype}-tableAriaLabel" table$id="{filetype}Table" id="{filetype}TableContainer">
                    <Head >
                        <Row>
                            {#each dataTableHead as item}
                                <Cell>{item}</Cell>
                            {/each}
                        </Row>
                    </Head>
                    <Body>
                        {#if show_dataTable_only_averaged}
                            {#each dataTable_avg as table, index (table.id)}
                                <Row>
                                    <Cell>Line #{index}</Cell>
                                    <Cell>{table.freq}</Cell>
                                    <Cell>{table.amp}</Cell>
                                    <Cell>{table.fwhm}</Cell>
                                    <Cell>{table.sig}</Cell>
                                </Row>
                            {/each}
                        {:else}
                            {#each dataTable as table (table.id)}
                                <Row style="background-color: {table.color};">
                                    <Cell>{table.name}</Cell>
                                    <Cell>{table.freq}</Cell>
                                    <Cell>{table.amp}</Cell>
                                    <Cell>{table.fwhm}</Cell>
                                    <Cell>{table.sig}</Cell>
                                </Row>
                            {/each}
                        {/if}
                    </Body>
                </DataTable>

            </div>

            <ReportLayout bind:currentLocation={currentLocation} 
                id="felixreport", plotID={["bplot", "saPlot", "avgplot", "exp-theory-plot"]} 
                includeTable={true}/>
        {/if}
    </div>
</Layout>