
<script>
    import {opoMode, toggleRow, felixOutputName, felixPlotAnnotations, felixPeakTable, expfittedLines, expfittedLinesCollectedData, fittedTraceCount, felixopoLocation} from "../../functions/svelteWritables";
    import Textfield from '@smui/textfield';
    import CustomIconSwitch from '../../../../components/CustomIconSwitch.svelte';
    import FelixPlotting from '../../modals/FelixPlotting.svelte';

    import {felix_func} from '../../functions/felix';

    export let felixPlotCheckboxes, preModal, felixfiles, graphPlotted, opofiles, normMethod, show_theoryplot, removeExtraFile, theoryLocation;

    let active=false, openShell=false, delta=1;

    let felixPlotWidgets = {

        text:[

            {label:"Fig. caption", value:" ", id:getID()},
            
            {label:"Fig. title", value:" ", id:getID()},
            {label:"Exp. title", value:" ", id:getID()},
            {label:"Exp. legend", value:" ", id:getID()},
            {label:"Cal. title", value:" ", id:getID()},
            {label:"markers", value:" ", id:getID()},
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
                removeExtraFile()
                graphPlotted = false, $felixOutputName = "averaged", $felixPlotAnnotations = [], $felixPeakTable = []
                if(felixfiles.length<1) return window.createToast("No files selected", "danger")
                
                pyfile="normline.py" , args=[...felixfiles, delta]

                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    $expfittedLines = [], $felixPlotAnnotations = [], $expfittedLinesCollectedData = [], $fittedTraceCount = 0
                    
                    show_theoryplot = false
                    felix_func({normMethod, dataFromPython, delta})
                    window.createToast("Graph Plotted", "success")
                    graphPlotted = true
                }).catch(err=>{preModal.modalContent = err;  preModal.open = true})

                break;
            
            case "baseline":
                if ($opoMode) {if(opofiles.length<1) return window.createToast("No OPO files selected", "danger")}
                else {if(felixfiles.length<1) return window.createToast("No FELIX files selected", "danger")}
                pyfile="baseline.py", args= $opoMode ? opofiles: felixfiles
                computePy_func({e, pyfile, args, general:true, openShell})
                .catch(err=>{preModal.modalContent = err;  preModal.open = true})
                break;

            case "matplotlib":
                const numberWidgets = felixPlotWidgets.number.map(n=>n.value)

                const textWidgets = felixPlotWidgets.text.map(n=>n.value)
                
                const booleanWidgets = felixPlotWidgets.boolean.map(n=>n.value)
                const selectedWidgets = felixPlotCheckboxes.map(n=>n.selected)

                pyfile="felix_tkplot.py", args=[JSON.stringify({numberWidgets, textWidgets, booleanWidgets, selectedWidgets, location: $felixopoLocation, normMethod, theoryLocation})]
                computePy_func({e, pyfile, args, general:true, openShell})
                .catch(err=>{preModal.modalContent = err;  preModal.open = true})


            default:
                break;
        }

    }

</script>


<FelixPlotting bind:active bind:felixPlotWidgets {felixPlotCheckboxes} on:submit="{(e)=>plotData({e:e.detail.event, filetype:"matplotlib"})}"/>

<div class="align">

    <button class="button is-link" id="create_baseline_btn" on:click="{(e)=>plotData({e:e, filetype:"baseline"})}"> Create Baseline</button>
    <button class="button is-link" id="felix_plotting_btn" on:click="{(e)=>plotData({e:e, filetype:"felix"})}">FELIX Plot</button>
    <Textfield style="width:7em" variant="outlined" type="number" step="0.5" bind:value={delta} label="Delta"/>
    <button class="button is-link" on:click="{()=>active = true}"> Open in Matplotlib</button>
    <CustomIconSwitch bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
    <button class="button is-link" on:click="{()=>$toggleRow = !$toggleRow}">Add Theory</button>
    <button class="button is-link" on:click="{()=>{$opoMode = !$opoMode}}">OPO</button>
</div>