
<script>
    import {opoMode, toggleRow, felixOutputName, felixPlotAnnotations, felixPeakTable, expfittedLines, expfittedLinesCollectedData, fittedTraceCount, dataTable, dataTable_avg} from "../../functions/svelteWritables";
    import Textfield from '@smui/textfield';
    import CustomIconSwitch from '../../../../components/CustomIconSwitch.svelte';
    import FelixPlotting from '../../modals/FelixPlotting.svelte';
    import {computePy_func} from '../../functions/computePy';

    import {felix_func} from '../../functions/felix';
    import {createToast} from '../../functions/misc';

    export let felixPlotCheckboxes, preModal, felixfiles, graphPlotted, opofiles, normMethod, show_theoryplot, removeExtraFile;

    let active=false, openShell=false, delta=1;

    let felixPlotWidgets = {

        text:[
            {label:"Fig. caption", value:"", id:getID()},
            {label:"Fig. title", value:"", id:getID()},
            {label:"Exp. title", value:"", id:getID()},
            {label:"Exp. legend", value:"", id:getID()},
            {label:"Cal. title", value:"", id:getID()},
            {label:"markers", value:"", id:getID()},
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
            {label:"Only exp.", value:false, id:getID()},
        
            
            {label:"hide ax2 axis.", value:true, id:getID()},
        
        ], checkBoxes: felixPlotCheckboxes
    }

    function plotData({e=null, filetype="felix"}={}){
        
        
        let pyfile="", args;
        
        switch (filetype) {

            case "felix":
                removeExtraFile()
                graphPlotted = false, $felixOutputName = "averaged", $felixPlotAnnotations = [], $felixPeakTable = []
                if(felixfiles.length<1) return createToast("No files selected", "danger")
                
                pyfile="normline.py" , args=[...felixfiles, delta]

                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    $expfittedLines = [], $felixPlotAnnotations = [], $expfittedLinesCollectedData = [], $fittedTraceCount = 0
                    show_theoryplot = false
                    // if (!keepTable) {$dataTable = $dataTable_avg = []}
                    felix_func({normMethod, dataFromPython, delta})
                    createToast("Graph Plotted", "success")
                    graphPlotted = true
                }).catch(err=>{preModal.modalContent = err;  preModal.open = true})

                break;
            
            case "baseline":
                if ($opoMode) {if(opofiles.length<1) return createToast("No OPO files selected", "danger")}
                else {if(felixfiles.length<1) return createToast("No FELIX files selected", "danger")}
                pyfile="baseline.py", args= $opoMode ? opofiles: felixfiles
                computePy_func({pyfile, args, general:true, openShell})
                .catch(err=>{preModal.modalContent = err;  preModal.open = true})
                break;

            default:
                break;
        }

    }

</script>


<FelixPlotting bind:active bind:felixPlotWidgets on:submit="{()=>console.log("FELIX plotting submitted", felixPlotWidgets) }"/>

<div class="align">

    <button class="button is-link" id="create_baseline_btn" on:click="{(e)=>plotData({e:e, filetype:"baseline"})}"> Create Baseline</button>
    <button class="button is-link" id="felix_plotting_btn" on:click="{(e)=>plotData({e:e, filetype:"felix"})}">FELIX Plot</button>
    <Textfield style="width:7em" variant="outlined" type="number" step="0.5" bind:value={delta} label="Delta"/>
    <button class="button is-link" on:click="{()=>active = true}"> Open in Matplotlib</button>
    <CustomIconSwitch bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
    <button class="button is-link" on:click="{()=>$toggleRow = !$toggleRow}">Add Theory</button>
    <button class="button is-link" on:click="{()=>{$opoMode = !$opoMode}}">OPO</button>
</div>