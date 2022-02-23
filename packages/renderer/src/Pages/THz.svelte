<script>
    import {relayout}               from 'plotly.js/dist/plotly-basic';
    import {plot, plotlyEventsInfo} from "$src/js/functions"
    import computePy_func           from "$src/Pages/general/computePy"
    import Layout                   from "$components/Layout.svelte"
    import CustomCheckbox           from "$components/CustomCheckbox.svelte"
    import CustomTextSwitch         from "$components/CustomTextSwitch.svelte"
    import CustomSelect             from "$components/CustomSelect.svelte"
    import Table                    from "$components/Table.svelte"
    import THzFitParamsTable        from "./thz/components/THzFitParamsTable.svelte"
    import {onDestroy}              from "svelte";
    /////////////////////////////////////////////////////////////////////////

    const filetype = "thz", id = "THz"

    let fileChecked = [];
    let currentLocation = ""
    $: thzfiles = fileChecked.map(file=>pathResolve(currentLocation, file))
    
    let fG = 0
    let fL = 1
    let binSize=10
    let openShell = false
    let graphPlotted = false
    let binData = false, saveInMHz = false;

    let fittedParamsTable = []
    async function plotData({e=null, filetype="thz", tkplot=false, justPlot=false, general={} }={}){

        if (fileChecked.length === 0 && filetype === "thz") {return window.createToast("No files selected", "danger")}
        const thz_args = {thzfiles, binData, tkplot, fG, fL, binSize, justPlot, saveInMHz, paramsTable, fitfile, fitMethod}
        let pyfileInfo = {general,
            thz: {pyfile:"thz_scan" , args:[JSON.stringify(thz_args)]},
        }
        let {pyfile, args} = pyfileInfo[filetype]
        if (tkplot) {filetype = "general"}

        if (filetype == "general") {
            return computePy_func({e, pyfile, args, general:true, openShell})

        }
        const dataFromPython = await computePy_func({e, pyfile, args})
        if (filetype=="thz") {

            fittedParamsTable = dataFromPython?.fittedParamsTable || []
            console.table(fittedParamsTable)
            plot(`THz Scan: Depletion (%)`, "Frequency (GHz)", "Depletion (%)", dataFromPython["thz"], "thzPlot", null, true)
            plot(`THz Scan`, "Frequency (GHz)", "Counts", dataFromPython["resOnOff_Counts"], "resOnOffPlot", null, true)
            if (!justPlot) {
                let lines = [];
                for (let x in dataFromPython["shapes"]) { lines.push(dataFromPython["shapes"][x]) }
                let layout_update = { shapes: lines }
                relayout("thzPlot", layout_update)
            }
        
        }
        window.createToast("Graph plotted", "success")
        graphPlotted = true
    }
    let openTable = false;
    let paramsTable = []

    let fitfile = "", fitMethod="lorentz"
    $: console.log({fitfile})
    const graphIDs = ["thzPlot", "resOnOffPlot"]
    onDestroy(()=>{
        graphIDs.forEach(graphID=>{
            if($plotlyEventsInfo[graphID]) {$plotlyEventsInfo[graphID].eventCreated = false; $plotlyEventsInfo[graphID].annotations = []}
        })
    })

</script>

<THzFitParamsTable bind:active={openTable} bind:paramsTable {currentLocation} {fG} {fL} />

<Layout  {filetype} {graphPlotted} {id} bind:currentLocation bind:fileChecked >

    <svelte:fragment slot="buttonContainer">
        <div class="align v-center">

            <button class="button is-link" style="min-width: 7em;" on:click="{(e)=>{plotData({e:e, justPlot:true})}}">Plot</button>
            <CustomCheckbox bind:selected={binData} label="Bin" />
            <CustomCheckbox bind:selected={saveInMHz} label="saveInMHz" />
            <button class="button is-link" on:click="{(e)=>plotData({e:e, tkplot:true})}">Open in Matplotlib</button>
            <CustomTextSwitch bind:value={binSize} label="binSize (kHz)" step="0.1" />
        </div>

        <div class="align" style="justify-content: flex-end;">
        
            <i class="material-icons" on:click="{()=>openTable=true}">settings</i>
            <CustomSelect bind:picked={fitfile} label="fitfile" options={[...fileChecked, "averaged"]} />
            <CustomSelect bind:picked={fitMethod} label="fit method" options={["gaussian", "lorentz", "voigt"]} />
            <button class="button is-link" style="min-width: 7em;" on:click="{(e)=>{plotData({e:e})}}">Fit</button>
            <CustomTextSwitch bind:value={fG} label="fG (MHz)" step="0.1" />
            <CustomTextSwitch bind:value={fL} label="fL (MHz)" step="0.1" />
        
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer">
        <div id="resOnOffPlot" class="graph__div" ></div>
        <div id="thzPlot" class="graph__div" ></div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer_functions">
        <button class="button is-warning" 
            style="width: 10em; margin-left: auto;"
            on:click="{()=>{$plotlyEventsInfo['thzPlot'].annotations=[]; relayout('thzPlot', {annotations: []})}}">
            Clear Annotations
        </button>
    </svelte:fragment>


    <svelte:fragment slot="plotContainer_reports">
        {#if fittedParamsTable.length>0}
             <Table head={Object.keys(fittedParamsTable[0])} keys={Object.keys(fittedParamsTable[0])} rows={fittedParamsTable} >
            </Table>
        {/if}
    </svelte:fragment>

</Layout>
