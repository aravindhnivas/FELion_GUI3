
<script>
    import {
        opoMode, toggleRow, felixOutputName, felixPlotAnnotations, felixPeakTable, expfittedLines, expfittedLinesCollectedData, fittedTraceCount, felixopoLocation, felixPlotCheckboxes, felixConfigDB, baselineFile
    } from "../../functions/svelteWritables";
    import {mainPreModal} from "../../../../svelteWritable";
    import Textfield from '@smui/textfield';
    import CustomIconSwitch from 'components/CustomIconSwitch.svelte';
    import FelixPlotting from '../../modals/FelixPlotting.svelte';
    import {felix_func} from '../../functions/felix';
    export let felixfiles, graphPlotted, opofiles, normMethod, show_theoryplot, removeExtraFile, theoryLocation;
    let active=false, openShell=false, delta=1;

    export let updateConfig=false;

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

    function plotData({e=null, filetype="felix"}={}){
        
        
        let pyfile="", args;
        
        switch (filetype) {

            case "felix":
                if(felixfiles.length<1) return window.createToast("No files selected", "danger")

                removeExtraFile()
                graphPlotted = false, $felixOutputName = "averaged", $felixPlotAnnotations = [], $felixPeakTable = []
                
                pyfile="normline.py" , args=[...felixfiles, delta]

                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    $expfittedLines = [], $felixPlotAnnotations = [], $expfittedLinesCollectedData = [], $fittedTraceCount = 0
                    show_theoryplot = false
                    felix_func({normMethod, dataFromPython, delta})
                    window.createToast("Graph Plotted", "success")

                    graphPlotted = true
                }).catch(error=>{window.handleError(error); console.error("Error main: ", error.stack || error)})
                break;
            
            case "baseline":
                if(!$baselineFile) {
                    
                    return window.createToast("No files: ctrl + left-click to select file for baseline correction", "danger")
                }
                pyfile="baseline.py"
                args=[JSON.stringify({filename: pathJoin($felixopoLocation, $baselineFile)})]
                computePy_func({e, pyfile, args, general:true, openShell})
                .catch(error=>{window.handleError(error)})
                
                break;

            case "matplotlib":
                const numberWidgets = felixPlotWidgets.number.map(n=>n.value)
                const textWidgets = felixPlotWidgets.text.map(n=>n.value)

                const booleanWidgets = felixPlotWidgets.boolean.map(n=>n.value)
                const selectedWidgets = $felixPlotCheckboxes.map(n=>n.selected)

                pyfile="felix_tkplot.py", args=[JSON.stringify({numberWidgets, textWidgets, booleanWidgets, selectedWidgets, location: $felixopoLocation, normMethod, theoryLocation})]
                computePy_func({e, pyfile, args, general:true, openShell})
                    .catch(error=>{window.handleError(error)})
            default:
                break;
                
        }

    
    }



    let fdelta=$felixConfigDB.get("fdelta");
    function loadConfig() {
        fdelta =  $felixConfigDB.get("fdelta")
        console.log("fdelta updated", fdelta)
    }
    $: if(updateConfig) loadConfig()
</script>

<style>
    .tag {
        border-radius: 2em;

        margin: 0 1em;
    
    }
</style>

<FelixPlotting bind:active bind:felixPlotWidgets {theoryLocation} on:submit="{(e)=>plotData({e:e.detail.event, filetype:"matplotlib"})}" />


    
<div class="align">

    <button class="button is-link" id="create_baseline_btn" on:click="{(e)=>plotData({e:e, filetype:"baseline"})}"> Create Baseline <span class="tag is-warning " aria-label="ctrl + left-click to select file for baseline correction" data-cooltipz-dir="bottom" >b</span>
    </button>
    <button class="button is-link" id="felix_plotting_btn" on:click="{(e)=>plotData({e:e, filetype:"felix"})}">FELIX Plot</button>

    <Textfield style="width:7em" variant="outlined" input$type="number" input$step={fdelta} input$min="0" bind:value={delta} label="Delta"/>
    
    <button class="button is-link" on:click="{()=>active = true}"> Open in Matplotlib</button>
    <CustomIconSwitch bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
    <button class="button is-link" on:click="{()=>$toggleRow = !$toggleRow}">Add Theory</button>
    <button class="button is-link" on:click="{()=>{$opoMode = !$opoMode}}">OPO</button>
    
</div>