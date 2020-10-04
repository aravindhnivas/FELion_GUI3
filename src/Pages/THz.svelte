<script>

    //  Importing
    import Layout from "../components/Layout.svelte"
    import CustomIconSwitch from "../components/CustomIconSwitch.svelte"
    import CustomSelect from "../components/CustomSelect.svelte"
    import CustomSwitch from "../components/CustomSwitch.svelte"

    import ReportLayout from "../components/ReportLayout.svelte"
    import Textfield from '@smui/textfield'
    import {plot} from "../js/functions.js"
    import ROSAA from "./thz/ROSAA.svelte"

    /////////////////////////////////////////////////////////////////////////

    // Initialisation

    const filetype = "thz", id = "THz"
    let fileChecked = [];
    let currentLocation = localStorage[`${filetype}_location`] || ""
    $: thzfiles = fileChecked.map(file=>path.resolve(currentLocation, file))
    let openShell = false, graphPlotted = false
    let delta = 10, gamma = 0

    let B0=0, D0=0, H0=0, temp=300, totalJ=20

    // Depletion Row
    let toggleRow = false
    const style = "width:7em; height:3.5em; margin-right:0.5em"
    const btnClass = "button is-link"

    const plotStyle = ["", "lines", "markers", "lines+markers"]

    let plotStyleSelected = plotStyle[3], plotFill = true;

    let binData = false;

    const changePlotStyle = () => { Plotly.restyle("thzPlot", {mode:plotStyleSelected, fill: plotFill ? "tozeroy" : ""})}

    function plotData({e=null, filetype="thz", tkplot="run", justPlot=false, general={} }={}){

        if (fileChecked.length === 0 && filetype === "thz") {return window.createToast("No files selected", "danger")}

    
        let pyfileInfo = {general,
            thz: {pyfile:"thz_scan.py" , args:[...thzfiles, binData, delta, tkplot, gamma, justPlot]},
            boltzman: {pyfile:"boltzman.py" , args:[currentLocation, B0, D0, H0, temp, totalJ, tkplot]},
        }
        let {pyfile, args} = pyfileInfo[filetype]
        if (tkplot == "plot") {filetype = "general"}

        if (filetype == "general") {
            return computePy_func({e, pyfile, args, general:true, openShell}).catch(err=>{preModal.modalContent = err;  preModal.open = true})
        }

        computePy_func({e, pyfile, args})
            .then((dataFromPython)=>{
                if (filetype=="thz") {

                    plot(`THz Scan: Depletion (%)`, "Frequency (GHz)", "Depletion (%)", dataFromPython["thz"], "thzPlot")
                    plot(`THz Scan`, "Frequency (GHz)", "Counts", dataFromPython["resOnOff_Counts"], "resOnOffPlot")

                    if (!justPlot) {
                        let lines = [];

                        for (let x in dataFromPython["shapes"]) { lines.push(dataFromPython["shapes"][x]) }
                        let layout_update = {
                            shapes: lines
                        }
                        Plotly.relayout("thzPlot", layout_update)
                    }
                } else if (filetype == "boltzman") {
                    plot(`Boltzman Distribution`, "Rotational levels (J)", "Probability (%)", dataFromPython, "boltzman_plot");
                }
                window.createToast("Graph plotted", "success")
                
                graphPlotted = true
            }).catch(err=>{preModal.modalContent = err;  preModal.open = true})

        
    }

    let includePlotsInReport = [{id:"resOnOffPlot", include:false, label:"THz Res-ON/OFF"}, {id:"thzPlot", include:true, label:"Normalised THz Spectrum"}, {id:"boltzman_plot", include:false, label:"Boltzman plot"}]
    let preModal = {};

    let ROSAA_modal_active = false;

</script>
<style>
    .thz_buttonContainer {min-height: 5em;}

    .button {margin-right: 0.5em;}
    .buttonRow {margin-bottom: 1em!important; align-items: center;}
    .hide {display: none;}

    * :global(.mdc-select__native-control option) {color: black}

</style>

<ROSAA bind:active={ROSAA_modal_active} on:submit="{(e)=>{plotData({e:e.detail.e, filetype:"general", general:{pyfile:"ROSAA.py", args:[JSON.stringify(e.detail.conditions)]}})}}" />

<Layout bind:preModal {filetype} {id} bind:currentLocation bind:fileChecked>

    <div class="thz_buttonContainer" slot="buttonContainer">

        <div class="content align buttonRow">
            <button class="{btnClass}" on:click="{()=>{ROSAA_modal_active=true}}">ROSAA</button>

            <button class="{btnClass}" on:click="{(e)=>{plotData({e:e, justPlot:true})}}">Plot</button>

            <CustomSwitch bind:selected={binData} label="Bin" style="margin:0 1em;"/>
            <button class="{btnClass}" on:click="{(e)=>{plotData({e:e})}}">Fit</button>
            <button class="{btnClass}" on:click="{(e)=>plotData({e:e, tkplot:"plot"})}">Open in Matplotlib</button>
            <CustomIconSwitch style="padding:0;" bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <button class="{btnClass}" on:click="{()=>{toggleRow = !toggleRow}}">Boltzman</button>
            <Textfield type="number" style="width:4em; height:3.5em; margin-right:0.5em" bind:value={delta} label="Delta" />
            <Textfield type="number" style="width:4em; height:3.5em; margin-right:0.5em" bind:value={gamma} label="Gamma" />

            <div class="animated fadeIn" class:hide={!graphPlotted} on:change={changePlotStyle}>
                <CustomSelect options={plotStyle} bind:picked={plotStyleSelected} label="Plot Style"/>
                <CustomSwitch bind:selected={plotFill} label="Fill area"/>

            </div>

        </div>

        <div class="animated fadeIn buttonRow" class:hide={!toggleRow} >
            <Textfield type="number" {style} bind:value={B0} label="B0 (MHz)" />
            <Textfield type="number" {style} bind:value={D0} label="D0 (MHz)" />
            <Textfield type="number" {style} bind:value={H0} label="H0 (MHz)" />
            <Textfield type="number" {style}  bind:value={temp} label="Temp." />
            <Textfield type="number" {style}  bind:value={totalJ} label="Total J" />
            <button class="{btnClass}" on:click="{(e)=>plotData({e:e, filetype:"boltzman"})}">Submit</button>
            <button class="{btnClass}" on:click="{(e)=>plotData({e:e, filetype:"boltzman", tkplot:"plot"})}">Open in Matplotlib</button>
        </div>

    </div>

    <div style="margin-right: 1em;" slot="plotContainer">

        <!-- Plots -->
        
        <div id="resOnOffPlot" style="margin-bottom: 1em;"></div>
        <div id="thzPlot" style="margin-bottom: 1em;"></div>
        <div id="boltzman_plot" style="margin-bottom: 1em;"></div>

        <!-- Reports -->

        {#if graphPlotted}
            <div class="animated fadeIn" style="flex-direction:column ">
                <ReportLayout bind:currentLocation={currentLocation} id={`${filetype}_report`} {includePlotsInReport} />
            </div>
        {/if}

    </div>
</Layout>