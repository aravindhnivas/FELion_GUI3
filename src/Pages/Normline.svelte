<script>
    // IMPORTING Modules
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text/index'
    import Layout, {browse, createToast} from "../components/Layout.svelte"
    import { fly, fade } from 'svelte/transition'
    import Ripple from '@smui/ripple'

    import {activated, modalContent} from "../components/Modal.svelte"
    import {bindDialog, filelist, filelistBinded} from "../components/DialogChecklist.svelte"
    import IconButton, {Icon} from '@smui/icon-button'
    import {plot, subplot} from "../js/functions.js"

    import Radio from '@smui/radio'
    import FormField from '@smui/form-field'
    import { flip } from 'svelte/animate'

    import Select, {Option} from '@smui/select'
    import Switch from '@smui/switch'
    import DataTable, {Head, Body, Row, Cell} from '@smui/data-table'
    import Checkbox from '@smui/checkbox';
    import CustomCheckbox from '../components/CustomCheckbox.svelte';
    // import Level from '../components/Level.svelte';
    // window.jsPDF = require('../public/assets/js/jspdf.min.js')
	// window.html2canvas = require("../public/assets/js/html2canvas.min.js")
   ///////////////////////////////////////////////////////////////////////

    let filetype="felix", id="Normline", fileChecked=[], delta=1, toggleRow=false;

    $: felixfiles = fileChecked.map(file=>path.resolve(currentLocation, file))
    let plottedFiles = []
    let currentLocation = localStorage[`${filetype}_location`] || ""
    $: console.log(`${filetype} Update: \n${currentLocation}`)

    ///////////////////////////////////////////////////////////////////////

    // Theory file
    let sigma = 20, scale=1, thoeryfiles = [], theoryfile_location="";
    let theorylistDialog 
    let theoryfile_filtered;
    let show_theoryplot = false;
    $: console.log("Filtered theory files: ", theoryfile_filtered)

    const get_theoryfiles = () => {
        browse({dir:false}).then(result=>{
            if (!result.canceled) {
                let files = result.filePaths
                theoryfile_location = path.dirname(files[0])
                $filelist = thoeryfiles = files.map(file=>file = path.basename(file))
                $filelistBinded = []
                createToast("Theoryfiles selected", "success")
            }
        }).catch(err=>{$modalContent = err; $activated=true})
    }

    ///////////////////////////////////////////////////////////////////////
    
    let openShell = false;
    let normMethod = "Relative", normMethod_datas = {}
    let graphPlotted = false, overwrite_expfit = false
    let line = [], index = [], annotations = []
    let output_name = "averaged"

    let dataTableHead = ["Filename", "Line (cm-1)", "Frequency, Ampl., FWHM - (cm-1)"]
    let dataTable = [], showDataTable=false;

    const replot = () => {
     
        if (graphPlotted) {Plotly.react("avgplot", normMethod_datas[normMethod].data, normMethod_datas[normMethod].layout, { editable: true })}
    }
    localStorage["pythonpath"] = path.resolve("C:\\ProgramData\\Miniconda3\\python")
    localStorage["pythonscript"] = path.resolve(__dirname, "assets/python_files")

    function plotData(event=null, filetype="felix", general=null){

        if (fileChecked.length === 0) return createToast("No files selected", "danger")
        let target = event.target
        target.classList.toggle("is-loading")
        
        if (filetype == "felix") {graphPlotted = false, output_name = "averaged"}
        if (filetype == "exp_fit") {if (index.length < 2) {
            target.classList.toggle("is-loading")
            return createToast("Range not found!!. Select a range using Box-select", "danger")

        }}

        let pyfileInfo = {
        
            felix: {file:"normline.py" , args:[...felixfiles, delta]},
            exp_fit: {file:"exp_gauss_fit.py" , args:[...felixfiles, overwrite_expfit, output_name, normMethod, currentLocation, ...index]},
        }

        let pyfile = pyfileInfo[filetype].file
        let args = pyfileInfo[filetype].args

        if (filetype == "general") {

            console.log("Sending general arguments: ", general.args)
            spawn(
                localStorage["pythonpath"],
                ["-i", path.join(localStorage["pythonscript"], general.pyfile), ...general_args],
                {
                    detached: true,
                    stdio: 'ignore',
                    shell: openShell
                }
            )
            py.unref()
            createToast("General process sent. Expect an response soon...")
            return;
        }

        let py;
        try {

            py = spawn( localStorage["pythonpath"], [path.resolve(localStorage["pythonscript"], pyfile), args] )
            createToast("Process Started")
        } catch (err) { $modalContent = err; $activated = true }

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
                        
                        dataTable = [...dataTable, {name: output_name, freq:dataFromPython["freq"], line: dataFromPython["fit"].name}]

                        console.log("Line fitted")
                        createToast("Line fitted with gaussian function", "success")
                    }
                
                } catch (err) { $modalContent = err; $activated = true }
            }
            // if (filetype == "exp_fit") {dataTable = dataTable.sort((x, y)=>x[0]-y[0])}
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

        Plotly.deleteTraces("avgplot", [-1])
        console.log("Last fitted peak removed")
        } else {
        if (annotations.length === 0) {createToast("No fitted lines found", "danger")}
        console.log("No line fit is found to remove")
        }
        
        line = line.slice(0, line.length - 2)
        annotations = annotations.slice(0, annotations.length - 1)
        index = []
        Plotly.relayout("avgplot", { annotations: annotations, shapes: line })
        if (line.length === 0) {ready_to_fit = false}
    }


    let reportTitle = "", reportComments = "", reportMethod = "info"
    let include_table = true, include_avgplot = true, include_saplot = false, include_bplot = false;
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
</style>

<Layout {filetype} {id} bind:currentLocation bind:fileChecked>

    <div class="buttonSlot" slot="buttonContainer">

        <div class="align" >

            <button class="button is-link">Create Baseline</button>
            <button class="button is-link" on:click="{(e)=>plotData(e, "felix")}">FELIX Plot</button>
            <button class="button is-link" use:Ripple={[true, {color: 'primary'}]} tabindex="0" on:click="{()=>toggleRow = !toggleRow}">Add Theory</button>
            <button class="button is-link">Open in Matplotlib</button>
            <button class="button is-link" on:click="{(e)=>plotData(e, "opo")}">OPO</button>
            <div class="short-input"><Textfield variant="outlined" bind:value={delta} label="Delta" /></div>
            <div><IconButton toggle bind:pressed={openShell}>
                    <Icon class="material-icons">code</Icon>
                    <Icon class="material-icons" on>settings_ethernet</Icon>
            </IconButton></div>

        </div>

        {#if toggleRow}
            <div class="align" transition:fly="{{ y: -20, duration: 500 }}">
                <button class="button is-link" on:click={get_theoryfiles}>Browse File</button>
                <button class="button is-link" on:click={$bindDialog.open}>Show files</button>
                <div class="short-input"><Textfield variant="outlined" bind:value={sigma} label="Sigma" /></div>
                <div class="short-input"><Textfield variant="outlined" bind:value={scale} label="Scale" /></div>
                <button class="button is-link">Open in Matplotlib</button>
                <button class="button is-link">Submit</button>
            </div>
        {/if}


        <div class="align" on:change={replot}>
            {#each ["Log", "Relative", "IntensityPerPhoton"] as method}
                <FormField >
                    <Radio bind:group={normMethod} value={method}  />
                    <span slot="label">{method}</span>
                </FormField>
            {/each}
        </div>

    </div>

    <div class="plotSlot" slot="plotContainer">

        {#if show_theoryplot}
            <div id="exp-theory-plot" transition:fade></div>
        {/if}
    
        <div id="bplot"></div>
        <div id="saPlot"></div>
        <div id="avgplot"></div>

        {#if graphPlotted}
            
            <!-- Pos-processing felix data -->
            <div transition:fade>
                <Select bind:value={output_name} label="Output filename">
                    {#each ["averaged", ...plottedFiles] as file}
                        <Option value={file} selected={output_name === file}>{file}</Option>
                    {/each}
                </Select>
                <FormField style="margin: 0 1em; padding-bottom: 1em;">
                    <Switch bind:checked={overwrite_expfit} />
                    <span slot="label">Overwrite</span>
                </FormField>
                <button class="button is-link" on:click="{(e)=>plotData(e, "exp_fit")}">Exp Fit.</button>
                <button class="button is-warning" on:click={clearLastPeak}>Clear Last</button>
                <button class="button is-danger" on:click={clearAllPeak}>Clear All</button>
                <button class="button is-danger" on:click="{()=>dataTable = []}">Clear Table</button>
            </div>

            <!-- Frequency table list -->
            <div class=""><h1 class="mdc-typography--headline4">Frequency table</h1></div>
            <hr>
            
            <div class="dataTable" transition:fade>

                <DataTable table$aria-label="felixfile line-list" table$id="felixTable">
                    <Head>
                        <Row>
                            {#each dataTableHead as item}
                                <Cell >{item}</Cell>
                            {/each}
                        </Row>
                    </Head>
                    <Body>
                    {#each dataTable.sort((x, y)=>x[1]-y[1]) as table (table.freq)}
                        <Row>
                            <Cell>{table.name}</Cell>
                            <Cell>{table.freq}</Cell>
                            <Cell>{table.line}</Cell>
                        </Row>
                    {/each}
                    </Body>
                </DataTable>
            
            </div>

            <!-- Add to report/notes taking section -->
            <div class=""><h1 class="mdc-typography--headline4">Add to report</h1></div>
            <hr>

            <div class="align report" id="felixreport" >
                {#each [{name:"info", color:"white"}, {name:"warning", color:"yellow"}, {name:"danger", color:"red"}] as method}
                    <FormField >
                        <Radio bind:group={reportMethod} value={method.name}  />
                        <span slot="label" style="color:{method.color}">{method.name}</span>
                    </FormField>
                {/each}
                <CustomCheckbox bind:selected={include_table} label={"Include table"}/>
                <CustomCheckbox bind:selected={include_avgplot} label={"Final plot"}/>
                <CustomCheckbox bind:selected={include_bplot} label={"Original plot"}/>
                <CustomCheckbox bind:selected={include_saplot} label={"Power & SA plot"}/>
                <Textfield style="height:3em; margin-bottom:1em;" variant="outlined" bind:value={reportTitle} label="Title" />
                <Textfield textarea bind:value={reportComments} label="Comments"  
                    input$aria-controls="felixreport_comments" input$aria-describedby="felixreport_comments"/>
                <HelperText id="felixreport_comments">
                    NOTE: You can write in markdown format (eg: # Title, **bold**, __italics__, 1., 2. for list, etc.,)
                </HelperText>
                <button class="button is-link">Add to Report</button>
                <button class="button is-link">Show Report</button>
            </div>
        {/if}
    
    </div>

</Layout>