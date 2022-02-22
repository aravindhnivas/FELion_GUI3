<script>
    import Textfield            from '@smui/textfield'
    import Layout               from "$components/Layout.svelte"
    import CustomTextSwitch     from "$components/CustomTextSwitch.svelte"
    import CustomSelect         from "$components/CustomSelect.svelte"
    import CustomCheckbox       from "$components/CustomCheckbox.svelte"
    import CustomIconSwitch     from "$components/CustomIconSwitch.svelte"
    import {plot}               from "../js/functions.js"
    // import ROSAA                from "./thz/ROSAA.svelte"
    import {relayout, restyle}  from 'plotly.js/dist/plotly-basic';
    import computePy_func       from "$src/Pages/general/computePy"
    
    /////////////////////////////////////////////////////////////////////////

    // Initialisation

    const filetype = "thz", id = "THz"
    let fileChecked = [];
    let currentLocation = ""
    $: thzfiles = fileChecked.map(file=>pathResolve(currentLocation, file))
    let openShell = false, graphPlotted = false
    let binSize=10, fG = 0, fL = 1

    const btnClass = "button is-link"

    const plotStyle = ["", "lines", "markers", "lines+markers"]

    let plotStyleSelected = plotStyle[3], plotFill = true;

    let binData = false, saveInMHz = false;

    const changePlotStyle = () => { restyle("thzPlot", {mode:plotStyleSelected, fill: plotFill ? "tozeroy" : ""})}

    function plotData({e=null, filetype="thz", tkplot=false, justPlot=false, general={} }={}){

        if (fileChecked.length === 0 && filetype === "thz") {return window.createToast("No files selected", "danger")}

    
        const thz_args = {thzfiles, binData, tkplot, fG, fL, binSize, justPlot, saveInMHz}
        let pyfileInfo = {general,
            thz: {pyfile:"thz_scan" , args:[JSON.stringify(thz_args)]},
        }
        let {pyfile, args} = pyfileInfo[filetype]
        if (tkplot) {filetype = "general"}

        if (filetype == "general") {
            return computePy_func({e, pyfile, args, general:true, openShell})

        }
        computePy_func({e, pyfile, args})
            .then((dataFromPython)=>{
                if (filetype=="thz") {

                    plot(`THz Scan: Depletion (%)`, "Frequency (GHz)", "Depletion (%)", dataFromPython["thz"], "thzPlot")
                    plot(`THz Scan`, "Frequency (GHz)", "Counts", dataFromPython["resOnOff_Counts"], "resOnOffPlot")
                    if (!justPlot) {
                        let lines = [];
                        for (let x in dataFromPython["shapes"]) { lines.push(dataFromPython["shapes"][x]) }
                        let layout_update = { shapes: lines }
                        relayout("thzPlot", layout_update)
                    }
                }
                window.createToast("Graph plotted", "success")
                graphPlotted = true
            })
    }

</script>

<Layout  {filetype} {graphPlotted} {id} bind:currentLocation bind:fileChecked>

    <svelte:fragment slot="buttonContainer">
        <div class="align v-center">
            <button class="{btnClass}" on:click="{(e)=>{plotData({e:e, justPlot:true})}}">Plot</button>
            <CustomCheckbox bind:selected={binData} label="Bin" />
            <CustomCheckbox bind:selected={saveInMHz} label="saveInMHz" />
            <button class="{btnClass}" on:click="{(e)=>{plotData({e:e})}}">Fit</button>
            <button class="{btnClass}" on:click="{(e)=>plotData({e:e, tkplot:true})}">Open in Matplotlib</button>
            <CustomIconSwitch style="padding:0;" bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <CustomTextSwitch bind:value={binSize} label="binSize (kHz)" step="0.1" />
            <CustomTextSwitch bind:value={fG} label="fG (MHz)" step="0.1" />
            <CustomTextSwitch bind:value={fL} label="fL (MHz)" step="0.1" />
            <!-- <button class="{btnClass}" on:click="{()=>{ROSAA_modal_active=true}}">ROSAA mode</button> -->

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