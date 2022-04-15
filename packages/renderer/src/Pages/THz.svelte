<script>
    import {
        relayout, addTraces, deleteTraces, restyle
    }    from 'plotly.js/dist/plotly-basic';
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
    
    let binSize=10
    let binData = true
    let showall = false;
    let saveInMHz = false
    let showRawData = false
    let graphPlotted = false

    let fittedParamsTable = []
    const freqTableKeys = ["filename", "freq", "amp", "fG", "fL"]
    const tableHeader = ["Filename", "freq (MHz)", "amp", "fG (MHz)", "fL (MHz)"]
    let rawDataProcessed = {data: null}
    let dataProcessed = {}
    let numOfFittedLines = 0
    let dataReady = false

    async function plotData({e=null, filetype="thz", tkplot=false, justPlot=false, general={} }={}){

        if (fileChecked.length === 0 && filetype === "thz") {return window.createToast("No files selected", "danger")}
        const thz_args = {
            thzfiles, binData, tkplot, binSize, justPlot, saveInMHz,
            paramsTable, fitfile, fitMethod, varyAll, plotIndex
        }
        let pyfileInfo = {general,
            thz: {pyfile: "thz_scan" , args: thz_args},
        }
        let {pyfile, args} = pyfileInfo[filetype]
        if (tkplot) {filetype = "general"}

        
        if (filetype == "general") {
            return computePy_func({e, pyfile, args, general:true })
        }
        
        if(!justPlot && paramsTable.length<1) return window.createToast("No initial guesses were given", "danger")
        dataReady = false


        const dataFromPython = await computePy_func({e, pyfile, args})
        if(!dataFromPython) return

        const fitPlot = !justPlot

        if (filetype=="thz") {

            if(fitPlot) {
        
                const {averaged, individual} = dataFromPython["thz"]
                const fitDataProcessed = {...individual, ...averaged}
                addTraces("thzPlot", fitDataProcessed[fitfile+"_fit"])
                numOfFittedLines++;
                const receivedPramsTable = dataFromPython?.fittedParamsTable || []
                fittedParamsTable = [...fittedParamsTable, ...receivedPramsTable].map(row=>({...row, id:getID()}))

            } else {

                const {averaged, individual} = dataFromPython["thz"]
                dataProcessed = {...individual, ...averaged}
                rawDataProcessed.data = dataFromPython["resOnOff_Counts"]
                dataReady = true
                numOfFittedLines = 0
            }
            // window.createToast("Graph plotted", "success")
            graphPlotted = true
        
        }
    
    }

    let openTable = false;
    let paramsTable = []

    let fitfile = "averaged", fitMethod="lorentz"
    const graphIDs = ["thzPlot", "resOnOffPlot"]

    onDestroy(()=>{
        graphIDs.forEach(graphID=>{
            if($plotlyEventsInfo[graphID]) {
                $plotlyEventsInfo[graphID].eventCreated = false; $plotlyEventsInfo[graphID].annotations = []
            }
        })
    })

    let varyAll = true;
    const [title, xlabel, ylabel] = ["THz Scan: Depletion (%)", "Frequency (GHz)", "Depletion (%)"]
    
    $: if(showall && dataProcessed) {

        plot(title, xlabel, ylabel, dataProcessed, "thzPlot", null, true)
        if(!plotlySelectCreated) {makePlotlySelect()}

    } else if(plotfile && dataProcessed?.[plotfile] && graphPlotted) {
        const dataToPlot = {data: dataProcessed[plotfile]}
        plot(title, xlabel, ylabel, dataToPlot, "thzPlot", null, true)
        if(!plotlySelectCreated) {makePlotlySelect()}

    }

    $: if(showall && rawDataProcessed?.data) {

        plot("THz Scan", "Frequency (GHz)", "Counts", rawDataProcessed.data, "resOnOffPlot")

    } else if(plotfile!=="averaged" && rawDataProcessed?.data ){

        const dataToPlot = {}
        dataToPlot[`${plotfile}_On`] = rawDataProcessed.data[`${plotfile}_On`]
        dataToPlot[`${plotfile}_Off`] = rawDataProcessed.data[`${plotfile}_Off`]
        plot("THz Scan", "Frequency (GHz)", "Counts", dataToPlot, "resOnOffPlot")

    }

    let plotfile = "averaged"
    let plotIndex = []
    let plotlySelectCreated = false

    const makePlotlySelect = () => {
        const graphDIV = document.getElementById("thzPlot")
        graphDIV.on("plotly_selected", (data) => {
            try {
                if(!data) return
                console.log(data)

                const { range } = data
                plotIndex = range.x
                console.log(range, plotIndex)
            } catch (error) { window.handleError(error) }
        })
        console.log("plotlySelectCreated", plotlySelectCreated)
        plotlySelectCreated = true
    }    
    let display = db.get("active_tab") === id ? 'block' : 'none'
</script>

<THzFitParamsTable bind:active={openTable} bind:paramsTable bind:varyAll {currentLocation} {fitMethod}/>

<Layout {filetype} {graphPlotted} {id} {display} bind:currentLocation bind:fileChecked >

    <svelte:fragment slot="buttonContainer">
        <div class="align v-center">

            <button class="button is-link" style="min-width: 7em;" 
                on:click="{(e)=>{plotData({e:e, justPlot:true})}}">
                Plot
            </button>
            
            <CustomCheckbox bind:selected={binData} label="Bin" />
            <CustomCheckbox bind:selected={saveInMHz} label="saveInMHz" />
            <CustomCheckbox bind:selected={showRawData} label="showRawData" />
            
            <CustomCheckbox bind:selected={showall} label="show all" />
            <CustomSelect bind:picked={plotfile} label="plotfile" options={[...fileChecked, "averaged"]} />
            
            <button class="button is-link" on:click="{(e)=>plotData({e:e, tkplot:true})}">Open in Matplotlib</button>
        
            <CustomTextSwitch bind:value={binSize} label="binSize (kHz)" step="0.1" />
        
        </div>

        <div class="align" style="justify-content: flex-end;">

            <i class="material-icons" on:click="{()=>openTable=true}">settings</i>
            <CustomSelect bind:picked={fitfile} label="fitfile" options={[...fileChecked, "averaged"]} />
            <CustomSelect bind:picked={fitMethod} label="fit method" options={["gaussian", "lorentz", "voigt"]} />
            <button class="button is-link" style="min-width: 7em;" on:click="{(e)=>{plotData({e:e})}}">Fit</button>
        
        </div>
    
    </svelte:fragment>

    <svelte:fragment slot="plotContainer">
        <div id="resOnOffPlot" class="graph__div" class:hide={!showRawData} ></div>
        <div id="thzPlot" class="graph__div" ></div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer_functions">
    
        <div class="align">
            <button class="button is-warning" 
                on:click="{()=>{if(numOfFittedLines>0) {deleteTraces("thzPlot", -1); numOfFittedLines--;}}}">
                Clear last fit
            </button>
            <button class="button is-warning" 
                on:click="{
                    ()=>{$plotlyEventsInfo['thzPlot'].annotations=[]; relayout('thzPlot', {annotations: []})}
                }">
                Clear Annotations
            </button>

        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer_reports">
        
        <button class="button is-danger" 
            style="margin-left: auto; width: 7em;" 
            on:click="{()=>fittedParamsTable=[]}">
            Clear Table
        </button>
        <Table 
            keys={freqTableKeys}
            head={tableHeader}
            disableInput={true}
            addextraOption={false}
            bind:rows={fittedParamsTable}
        />
    </svelte:fragment>
</Layout>
