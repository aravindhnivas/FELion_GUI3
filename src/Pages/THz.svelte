<script>

    //  Importing
    import Layout from "../components/Layout.svelte"
    import CustomIconSwitch from "../components/CustomIconSwitch.svelte"
    import CustomSelect from "../components/CustomSelect.svelte"
    import CustomSwitch from "../components/CustomSwitch.svelte"

    import ReportLayout from "../components/ReportLayout.svelte"
    import Textfield from '@smui/textfield'
    import { fly, fade } from 'svelte/transition'
    import {plot, subplot} from "../js/functions.js"

    import {activated, modalContent} from "../components/Modal.svelte"
    import {createToast} from "../components/Layout.svelte"
    // import {afterUpdate} from "svelte"

    import {Icon} from '@smui/icon-button'
    /////////////////////////////////////////////////////////////////////////

    // Initialisation
    const filetype = "thz", id = "THz"
    let fileChecked = [];
    let currentLocation = localStorage[`${filetype}_location`] || ""
    $: thzfiles = fileChecked.map(file=>path.resolve(currentLocation, file))
    let openShell = false, graphPlotted = false
    let delta = 1, gamma = 0

    let B0=0, D0=0, H0=0, temp=300, totalJ=20

    // Depletion Row
    let toggleRow = false
    const style = "width:7em; height:3.5em; margin-right:0.5em"
    const btnClass = "button is-link animated"

    const plotStyle = ["", "lines", "markers", "lines+markers"]

    let plotStyleSelected = plotStyle[3]
    let plotFill = true;

    const changePlotStyle = () => { Plotly.restyle("thzPlot", {mode:plotStyleSelected, fill: plotFill ? "tozeroy" : ""})}
    function plotData({e=null, filetype="thz", tkplot="run", justPlot=false }={}){

        if (fileChecked.length === 0) {return createToast("No files selected", "danger")}

        let pyfileInfo = {
            thz: {pyfile:"thz_scan.py" , args:[...thzfiles, delta, tkplot, gamma, justPlot]},
            boltzman: {pyfile:"boltzman.py" , args:[currentLocation, B0, D0, H0, temp, totalJ, tkplot]},
        }
        let {pyfile, args} = pyfileInfo[filetype]
        if (tkplot == "plot") {filetype = "general"}

        if (filetype == "general") {
            console.log("Sending general arguments: ", args)
            let py = spawn(
                localStorage["pythonpath"],
                ["-i", path.join(localStorage["pythonscript"], pyfile), args],
                { detached: true, stdio: 'ignore', shell: openShell }
            )
            py.unref()
            createToast("General process sent. Expect an response soon...")
            return;
        }

        let target = e.target
        target.classList.toggle("is-loading")
        if (filetype == "scan") {graphPlotted = false}
        
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

        let error_occured_py = false

        py.stderr.on("data", err => {
            $modalContent = err
            $activated = true
            error_occured_py = true;
            target.style.backgroundColor="#ff3860"
            target.classList.add("shake")
        });

        py.on("close", () => {

            if (!error_occured_py) {

                try {
                    let dataFromPython = fs.readFileSync(path.join(localStorage["pythonscript"], "data.json"))
                    dataFromPython = JSON.parse(dataFromPython.toString("utf-8"))
                    console.log(dataFromPython)

                    if (filetype=="thz") {
                       plot(`THz Scan`, "Frequency (GHz)", "Depletion (%)", dataFromPython, "thzPlot");
    
                        let lines = [];

                        for (let x in dataFromPython["shapes"]) { lines.push(dataFromPython["shapes"][x]) }
                        let layout_update = {
                            shapes: lines
                        }
                        Plotly.relayout("thzPlot", layout_update)
                    } else if (filetype == "boltzman") {
                        plot(`Boltzman Distribution`, "Rotational levels (J)", "Probability (%)", dataFromPython, "boltzman_plot");
                    }
                    createToast("Graph plotted", "success")
                    graphPlotted = true

                    target.style.backgroundColor="#09814a"
                    target.classList.add("bounce")

                } catch (err) { 
                    $modalContent = err
                    $activated = true 

                    target.style.backgroundColor="#ff3860"
                    target.classList.add("shake")
                 }

            }

            console.log("Process closed")
            target.classList.toggle("is-loading")
            setTimeout(()=>{
                target.style.backgroundColor=""
                if (target.classList.contains("bounce")) target.classList.remove("bounce")
                if (target.classList.contains("shake")) target.classList.remove("shake")
            }, 2000)
        })
    }


</script>

<style>

    .thz_buttonContainer {min-height: 5em;}
    .button {margin-right: 0.5em;}
    .buttonRow {margin-bottom: 1em!important; align-items: center;}

    .active {display: flex!important;}
    .hide {display: none;}
    .align {display: flex; align-items: center;}
    * :global(.mdc-select__native-control option) {color: black}

    .plotStyleRow {
        align-items: center; justify-items: center;
        flex-direction: row-reverse; margin-bottom: 1em;
    }
    
    
</style>


<Layout {filetype} {id} bind:currentLocation bind:fileChecked>
    <div class="thz_buttonContainer" slot="buttonContainer">

        <div class="content align buttonRow">
            <button class="{btnClass}" on:click="{(e)=>{plotData({e:e, justPlot:true})}}">Plot</button>
            <button class="{btnClass}" on:click="{(e)=>{plotData({e:e})}}">Fit</button>
            <button class="{btnClass}" on:click="{(e)=>plotData({e:e, tkplot:"plot"})}">Open in Matplotlib</button>
            <CustomIconSwitch style="padding:0;" bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <button class="{btnClass}" on:click="{()=>{toggleRow = !toggleRow}}">Boltzman</button>
            <Textfield type="number" {style} on:change="{(e)=>plotData({e:e})}" bind:value={delta} label="Delta" />
            <Textfield type="number" {style} on:change="{(e)=>plotData({e:e})}" bind:value={gamma} label="Gamma" />
        </div>

        <div class="animated fadeIn hide buttonRow" class:active={toggleRow} >
            <Textfield {style} on:change="{(e)=>plotData({e:e, filetype:"boltzman"})}" bind:value={B0} label="B0 (MHz)" />
            <Textfield {style} on:change="{(e)=>plotData({e:e, filetype:"boltzman"})}" bind:value={D0} label="D0 (MHz)" />
            <Textfield {style} on:change="{(e)=>plotData({e:e, filetype:"boltzman"})}" bind:value={H0} label="H0 (MHz)" />
            <Textfield type="number" {style} on:change="{(e)=>plotData({e:e, filetype:"boltzman"})}" bind:value={temp} label="Temp." />
            <Textfield type="number" {style} on:change="{(e)=>plotData({e:e, filetype:"boltzman"})}" bind:value={totalJ} label="Total J" />
            <button class="{btnClass}" on:click="{(e)=>plotData({e:e, filetype:"boltzman"})}">Submit</button>
            <button class="{btnClass}" on:click="{(e)=>plotData({e:e, filetype:"boltzman", tkplot:"plot"})}">Open in Matplotlib</button>
        </div>

    </div>


    <div style="margin-right: 1em;" slot="plotContainer">

        <div class="content">

            <div class="plotStyleRow animated fadeIn hide" class:active={graphPlotted} on:change={changePlotStyle}>
                <CustomSwitch bind:selected={plotFill} label="Fill area"/>
                <CustomSelect options={plotStyle} bind:picked={plotStyleSelected} label="Plot Style"/>
            </div>
            <div id="thzPlot"></div>
        </div>
        
        <div id="boltzman_plot"></div>
        <div class="animated fadeIn hide" class:active={graphPlotted} style="flex-direction:column ">
            <ReportLayout bind:currentLocation id="thzreport", plotID={["thzPlot"]}/>
        </div>

    </div>
</Layout>