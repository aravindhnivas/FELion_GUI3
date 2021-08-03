<script>
    import {mainPreModal} from "../svelteWritable";
    //  Importing
    import Layout from "../components/Layout.svelte"
    import CustomIconSwitch from "../components/CustomIconSwitch.svelte"
    import CustomSelect from "../components/CustomSelect.svelte"
    import CustomCheckbox from "../components/CustomCheckbox.svelte"

    // import ReportLayout from "../components/ReportLayout.svelte"
    import Textfield from '@smui/textfield'
    import {plot} from "../js/functions.js"
    import ROSAA from "./thz/ROSAA.svelte"

    /////////////////////////////////////////////////////////////////////////

    // Initialisation

    const filetype = "thz", id = "THz"
    let fileChecked = [];
    let currentLocation = db.get(`${filetype}_location`) || ""
    $: thzfiles = fileChecked.map(file=>path.resolve(currentLocation, file))
    let openShell = false, graphPlotted = false
    let delta = 10, gamma = 0

    const btnClass = "button is-link"

    const plotStyle = ["", "lines", "markers", "lines+markers"]

    let plotStyleSelected = plotStyle[3], plotFill = true;

    let binData = false, saveInMHz = false;

    const changePlotStyle = () => { Plotly.restyle("thzPlot", {mode:plotStyleSelected, fill: plotFill ? "tozeroy" : ""})}

    function plotData({e=null, filetype="thz", tkplot=false, justPlot=false, general={} }={}){

        if (fileChecked.length === 0 && filetype === "thz") {return window.createToast("No files selected", "danger")}

    
        const thz_args = {thzfiles, binData, delta, tkplot, gamma, justPlot, saveInMHz}
        let pyfileInfo = {general,
            thz: {pyfile:"thz_scan.py" , args:[JSON.stringify(thz_args)]},
            boltzman: {pyfile:"boltzman.py" , args:[currentLocation, B0, D0, H0, temp, totalJ, tkplot]},
        }
        let {pyfile, args} = pyfileInfo[filetype]
        if (tkplot) {filetype = "general"}

        if (filetype == "general") {
            return computePy_func({e, pyfile, args, general:true, openShell}).catch(error=>{mainPreModal.error(error.stack || error)})
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
            }).catch(error=>{mainPreModal.error(error.stack || error)})

        
    }

    let includePlotsInReport = [{id:"resOnOffPlot", include:false, label:"THz Res-ON/OFF"}, {id:"thzPlot", include:true, label:"Normalised THz Spectrum"}, {id:"boltzman_plot", include:false, label:"Boltzman plot"}]

    let ROSAA_modal_active = false;

</script>
<style>

</style>
<ROSAA bind:active={ROSAA_modal_active}  />
<Layout  {filetype} {graphPlotted} {id} bind:currentLocation bind:fileChecked>

    <svelte:fragment slot="buttonContainer">
        <div class="align v-center">
            <button class="{btnClass}" on:click="{()=>{ROSAA_modal_active=true}}">ROSAA</button>
            <button class="{btnClass}" on:click="{(e)=>{plotData({e:e, justPlot:true})}}">Plot</button>
            <CustomCheckbox bind:selected={binData} label="Bin" />
            <CustomCheckbox bind:selected={saveInMHz} label="saveInMHz" />

            <button class="{btnClass}" on:click="{(e)=>{plotData({e:e})}}">Fit</button>
            <button class="{btnClass}" on:click="{(e)=>plotData({e:e, tkplot:true})}">Open in Matplotlib</button>
            <CustomIconSwitch style="padding:0;" bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <Textfield type="number" bind:value={delta} label="Delta" input$step="0.1" />
            <Textfield type="number" bind:value={gamma} label="Gamma" input$step="0.1" />

        </div>

    </svelte:fragment>

    <svelte:fragment slot="plotContainer">

        <!-- Plots -->
        <div id="resOnOffPlot" class="graph__div" ></div>

        {#if graphPlotted}

            <div class="animated fadeIn align h-end v-center" on:change={changePlotStyle}>
                <CustomSelect options={plotStyle} bind:picked={plotStyleSelected} label="Plot Style"/>
                <CustomCheckbox bind:selected={plotFill} label="Fill area"/>
            </div>
        
            {/if}
        
        <div id="thzPlot" class="graph__div" ></div>
    
    </svelte:fragment>
</Layout>