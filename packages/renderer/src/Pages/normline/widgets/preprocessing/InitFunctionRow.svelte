
<script>
    import {
        opoMode,
        showall,
        toggleRow,
        normMethod,
        baselineFile,
        felixPeakTable,
        expfittedLines,
        normMethodDatas,
        felixOutputName,
        fittedTraceCount,
        felixopoLocation,
        felixGraphPlotted,
        felixPlotCheckboxes,
        felixPlotAnnotations,
        expfittedLinesCollectedData,
    }                           from "../../functions/svelteWritables";
    import FelixPlotting        from '../../modals/FelixPlotting.svelte';
    import {felix_func}         from '../../functions/felix';
    import plotIndividualDataIntoGraph,
        {get_data, mapNormMethodKeys}   from '../../functions/plotIndividualDataIntoGraph';
    import CustomTextSwitch     from '$components/CustomTextSwitch.svelte'
    import { subplot, plot }    from "$src/js/functions.js";
    import computePy_func       from "$src/Pages/general/computePy"
    import {react}              from "plotly.js/dist/plotly-basic"


    ///////////////////////////////////////////////////////////////////////////

    export let plotfile="average"
    export let felixfiles=[]
    export let theoryLocation="";
    export let removeExtraFile
    ///////////////////////////////////////////////////////////////////////////
    
    let delta=1;
    let active=false
    let openShell=false

    let felixPlotWidgets = {
        text:[
            {label:"Fig. caption", value:"caption", id:getID()},
            {label:"Fig. title", value:"Title", id:getID()},
            {label:"Exp. title", value:"Exp. title", id:getID()},
            {label:"Exp. legend", value:"legend", id:getID()},
            {label:"Cal. title", value:"calc title", id:getID()},
            {label:"markers", value:":1", id:getID()},
        ],
    
        number:[
            {label:"Fig. Width", value:7, step:1, id:getID()},
            {label:"Fig. Height", value:7, step:1,  id:getID()},
            {label:"Fig. DPI", value:120, step:5,  id:getID()},
            {label:"freqScale", value:1, step:0.01,  id:getID()},
            {label:"gridAlpha", value:0, step:0.1,  id:getID()},
            {label:"theorySigma", value:5, step:1,  id:getID()},
            {label:"Tick Interval", value:200, step:50,  id:getID()},
        
        ],
        boolean:[
            {label:"sameColor", value:true, id:getID()},
            {label:"Invert ax2", value:true, id:getID()},
            {label:"Only exp.", value:true, id:getID()},
            {label:"hide ax2 axis.", value:true, id:getID()},
            {label:"hide_all_axis", value:false, id:getID()},
            {label:"legend_visible", value:true, id:getID()}

        ]
    }

    const fullData = {}
    let dataReady = false
    async function plotData({e=null, filetype="felix"}={}){
        
        let pyfile="", args;
        
        switch (filetype) {

            case "felix":
                if(felixfiles.length<1) return window.createToast("No files selected", "danger")
                removeExtraFile()
                dataReady = false

                pyfile="normline" 
                args=[JSON.stringify({felixfiles, delta})]

                $felixPeakTable = []
                $felixPlotAnnotations = []
                $felixOutputName = "averaged"

                const dataFromPython = await computePy_func({e, pyfile, args})
                if(!dataFromPython) return
                
                $expfittedLines = []
                $fittedTraceCount = 0
                $felixPlotAnnotations = []
                $expfittedLinesCollectedData = []
                
                // show_theoryplot = false
                fullData.data = dataFromPython
                dataReady = true

                break;
            
            case "baseline":
                if(!$baselineFile) {
                    return window.createToast("No files: ctrl + left-click to select file for baseline correction", "danger")
                }
                pyfile="baseline"
                args=[JSON.stringify({filename: pathJoin($felixopoLocation, $baselineFile)})]
                computePy_func({e, pyfile, args, general:true, openShell})
                break;

            case "matplotlib":
                const numberWidgets = felixPlotWidgets.number.map(n=>n.value)
                const textWidgets = felixPlotWidgets.text.map(n=>n.value)
                const booleanWidgets = felixPlotWidgets.boolean.map(n=>n.value)
                const selectedWidgets = $felixPlotCheckboxes.map(n=>n.selected)

                pyfile="felix_tkplot"
                args=[JSON.stringify({
                    numberWidgets, textWidgets, booleanWidgets, 
                    selectedWidgets, location: $felixopoLocation, 
                    normMethod: $normMethod, theoryLocation
                })]

                computePy_func({e, pyfile, args, general:true, openShell})
            default:
                break;
        }
    }

    $: updateplot = dataReady && plotfile && $normMethod && fullData.data && !$opoMode
    $: if(updateplot && $showall) {
        if($felixGraphPlotted) {
            const currentKey = mapNormMethodKeys[$normMethod]
            const currentData = get_data(fullData.data[currentKey])
            const {layout} = $normMethodDatas[$normMethod]
            react("avgplot", currentData, layout)

            plot( "Baseline Corrected", "Wavelength (cm-1)", "Counts", fullData.data["base"], "bplot" )
            subplot(
                "Spectrum and Power Analyser", 
                "Wavelength set (cm-1)", "SA (cm-1)", fullData.data["SA"], "saPlot",
                "Wavelength (cm-1)", `Total Power (mJ)`, fullData.data["pow"]
            );

        } else {
            felix_func({dataFromPython: fullData.data, delta})
            $felixGraphPlotted = true
        }
    } else if(updateplot) {
        console.log({$showall, plotfile})
        plotIndividualDataIntoGraph({fullData, plotfile, graphPlotted: $felixGraphPlotted, delta})
    } 



</script>

<FelixPlotting bind:active bind:felixPlotWidgets {theoryLocation} 
    on:submit="{(e)=>plotData({e:e.detail.event, filetype:"matplotlib"})}"
/>

<div class="align">
    <button class="button is-link" id="create_baseline_btn" on:click="{(e)=>plotData({e:e, filetype:"baseline"})}">
        Create Baseline
        <span class="tag is-warning " aria-label="ctrl + left-click to select file for baseline correction" data-cooltipz-dir="bottom" >b</span>
    </button>
    <button class="button is-link" id="felix_plotting_btn" on:click="{(e)=>plotData({e:e, filetype:"felix"})}">
        FELIX Plot
    </button>

    <CustomTextSwitch style="width:7em" variant="outlined" bind:value={delta} label="Delta" step="0.5" />
    <button class="button is-link" on:click="{()=>active = true}"> Open in Matplotlib</button>
    <button class="button is-link" on:click="{()=>$toggleRow = !$toggleRow}">Add Theory</button>
    <button class="button is-link" on:click="{()=>{$opoMode = !$opoMode}}">OPO</button>

</div>



<style>
    .tag {
        border-radius: 2em;
        margin: 0 1em;
    }    

</style>
