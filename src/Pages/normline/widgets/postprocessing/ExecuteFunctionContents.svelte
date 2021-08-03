
<script>

    import { fittedTraceCount, felixPlotAnnotations, felixIndex, expfittedLines, expfittedLinesCollectedData , graphDiv, dataTable, Ngauss_sigma, felixOutputName, felixPeakTable, felixopoLocation, felixAnnotationColor} from "../../functions/svelteWritables";
    import {mainPreModal} from "../../../../svelteWritable";
    import Textfield from '@smui/textfield';
    import CustomSwitch from '../../../../components/CustomSwitch.svelte';

    import {Icon} from '@smui/icon-button';

    import AdjustInitialGuess from "../../modals/AdjustInitialGuess.svelte";
    import {savefile, loadfile} from "../../functions/misc";
    
    import { fade } from 'svelte/transition';
    
    import {NGauss_fit_func} from '../../functions/NGauss_fit';
    
    import {find_peaks_func} from '../../functions/find_peaks';
    import {exp_fit_func} from '../../functions/exp_fit';
    import {get_err_func} from '../../functions/get_err';
    
    export let addedFileScale, addedFileCol, normMethod, writeFileName, writeFile, overwrite_expfit, fullfiles;
    
    let boxSelected_peakfinder=false, NGauss_fit_args={}

    let peak_height = 1, peak_width = 3, peak_prominence = 0;
    let toggleFindPeaksRow = false, savePeakfilename = "peakTable", modalActivate=false;

    const style = "width:7em; height:3.5em; margin-right:0.5em";

    const clearAllPeak = () => {
        if ($fittedTraceCount === 0) {return window.createToast("No fitted lines found", "danger")}

        console.log("Removing all found peak values")
        
        $felixPlotAnnotations = $felixIndex = $expfittedLines = $expfittedLinesCollectedData = []

        Plotly.relayout($graphDiv, { annotations: [], shapes: [] })
        
        for (let i=0; i<$fittedTraceCount; i++) {Plotly.deleteTraces($graphDiv, [-1])}
        
        $fittedTraceCount = 0
    }

    const clearLastPeak = () => {
        
        if ($fittedTraceCount === 0) {return window.createToast("No fitted lines found", "danger")}

        plotData({filetype:"general", general:{args:[$felixOutputName, $felixopoLocation, normMethod], pyfile:"delete_fileLines.py"}})
        $dataTable = _.dropRight($dataTable, 1)
        $expfittedLines = _.dropRight($expfittedLines, 2)
        $felixPlotAnnotations = _.dropRight($felixPlotAnnotations, 1)
        $expfittedLinesCollectedData = _.dropRight($expfittedLinesCollectedData, 1)
        Plotly.relayout($graphDiv, { annotations: $felixPlotAnnotations, shapes: $expfittedLines })

        Plotly.deleteTraces($graphDiv, [-1])
        console.log("Last fitted peak removed")
        $fittedTraceCount--

    }

    function loadpeakTable(){
        const loadedfile = loadfile({name:savePeakfilename})
        $felixPeakTable = _.uniqBy([...loadedfile, ...$felixPeakTable], "freq")
        adjustPeak()

    }

    function adjustPeak({closeMainModal=true}={}) {
        $felixPeakTable = _.filter($felixPeakTable, (tb)=>tb.sig != 0);
        
        $felixPeakTable = _.sortBy($felixPeakTable, [(o)=>o["freq"]])

        let temp_annotate = {xref:"x", y:"y", "showarrow":true,  "arrowhead":2, "ax":-25, "ay":-40, font:{color:$felixAnnotationColor}, arrowcolor:$felixAnnotationColor}

        
        $felixPlotAnnotations = $felixPeakTable.map((f)=>{
        
            const {freq, amp} = f

            const x = parseFloat(freq)

            const y = parseFloat(amp)
            let _annotate = {x, y, text:`(${x.toFixed(2)}, ${y.toFixed(2)})`}
            
            return {...temp_annotate, ..._annotate}
        
        })

        if(closeMainModal) {
            modalActivate = false, window.createToast("Initial guess adjusted for full spectrum fitting")
        }
        Plotly.relayout($graphDiv, { annotations:$felixPlotAnnotations })
    };

    function plotData({e=null, filetype="exp_fit", general={}}={}){

        if (filetype == "general") {
            const {pyfile, args} = general

            computePy_func({pyfile, args, general:true})
            .catch(error=>{mainPreModal.error(error.stack || error)})
            return;
        
        }

        let pyfile="", args;
        let expfit_args = [], find_peaks_args = {}
        
        switch (filetype) {

            case "exp_fit":
                if ($felixIndex.length<2) { return window.createToast("Range not found!!. Select a range using Box-select", "danger") }

                expfit_args = { addedFileScale, addedFileCol, output_name:$felixOutputName, overwrite_expfit, writeFile, writeFileName, normMethod, index:$felixIndex, fullfiles, location:$felixopoLocation }

                pyfile="exp_gauss_fit.py" , args=[JSON.stringify(expfit_args)]
                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    exp_fit_func({dataFromPython})
                    window.createToast("Line fitted with gaussian function", "success")
                }).catch(error=>{mainPreModal.error(error.stack || error)})

                break;

            case "NGauss_fit":

                if (boxSelected_peakfinder) {
                    if ($felixIndex.length<2) { return window.createToast("Box selection is turned ON so please select a wn. range to fit", "danger") }
                    NGauss_fit_args.index = $felixIndex

                } else {delete NGauss_fit_args.index}


                
                if ($felixPeakTable.length === 0) {return window.createToast("No arguments initialised yet.", "danger") }
                
                NGauss_fit_args.fitNGauss_arguments = {}
                $felixPeakTable = _.sortBy($felixPeakTable, [(o)=>o["freq"]])

                $felixPeakTable.forEach((f, index)=>{
                    NGauss_fit_args.fitNGauss_arguments[`cen${index}`] = f.freq
                    NGauss_fit_args.fitNGauss_arguments[`A${index}`] = f.amp

                    NGauss_fit_args.fitNGauss_arguments[`sigma${index}`] = f.sig
                })

                NGauss_fit_args = {...NGauss_fit_args, location:$felixopoLocation, addedFileScale, addedFileCol, overwrite_expfit, writeFile, writeFileName, output_name:$felixOutputName, fullfiles, normMethod}
                pyfile="multiGauss.py" , args=[JSON.stringify(NGauss_fit_args)]

                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    NGauss_fit_func({dataFromPython})
                    console.log("Line fitted")
                    window.createToast(`Line fitted with ${dataFromPython["fitted_parameter"].length} gaussian function`, "success")
                }).catch(error=>{mainPreModal.error(error.stack || error)})
                break;
            
            case "find_peaks":
                
                $felixPeakTable = []

                if ($felixIndex.length<2 && boxSelected_peakfinder) { return window.createToast("Box selection is turned ON so please select a wn. range to fit", "danger") }
                
                let selectedIndex = boxSelected_peakfinder ? $felixIndex : [0, 0]
                find_peaks_args = { addedFileScale, addedFileCol, output_name:$felixOutputName, normMethod, peak_prominence, peak_width, peak_height, selectedIndex, fullfiles, location:$felixopoLocation }



                pyfile="fit_all.py" ,  args=[JSON.stringify(find_peaks_args)]

                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    find_peaks_func({dataFromPython})
                    console.log(`felixPeakTable:`, $felixPeakTable)
                    window.createToast("Peaks found", "success")
                }).catch(error=>{mainPreModal.error(error.stack || error)})

                break;

            case "get_err":
                if ($expfittedLinesCollectedData.length<2) return window.createToast("Not sufficient lines collected!", "danger")
                pyfile="weighted_error.py" , args=$expfittedLinesCollectedData
                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    get_err_func({dataFromPython})
                    window.createToast("Weighted fit. done", "success")
                }).catch(error=>{mainPreModal.error(error.stack || error)})
                break;

         
            default:
                break;
        }

    }

    $: $felixPeakTable = $felixPeakTable.map((f)=>{
        
            let {freq, amp, sig, id} = f
            freq = parseFloat(freq)
            amp = parseFloat(amp)
            sig = parseFloat(sig)
            return {freq, amp, sig, id}
    })

</script>

<AdjustInitialGuess bind:active={modalActivate} on:save={adjustPeak}/>


<div class="align">
    <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"exp_fit"})}">Exp Fit.</button>
    <button class="button is-link" on:click="{()=>toggleFindPeaksRow = !toggleFindPeaksRow}">Fit NGauss.</button>
    <button class="button is-warning" on:click={clearLastPeak}>Clear Last</button>
    <button class="button is-danger" on:click={clearAllPeak}>Clear All</button>
    <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"get_err"})}">Weighted Mean</button>
    <button class="button is-warning" on:click="{()=>{$expfittedLinesCollectedData = []; window.createToast("Line collection restted", "warning")}}">Reset</button>

</div>

<!-- Fit peaks functions -->

{#if toggleFindPeaksRow}

    <div transition:fade>
        <div class="align">
        
            <CustomSwitch style="margin: 0 1em;" bind:selected={boxSelected_peakfinder} label="BoxSelected"/>
            <Textfield type="number" {style} step="0.5" bind:value={peak_prominence} label="Prominance" />
            <Textfield type="number" {style} step="0.5" bind:value={peak_width} label="Width" />

            <Textfield type="number" {style} step="0.1" bind:value={peak_height} label="Height" />
            <Textfield style="width:9em" bind:value={$Ngauss_sigma} label="Sigma"/>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"find_peaks"})}">Get Peaks</button>
        </div>
        
        <div class="align" >
            <Icon class="material-icons" on:click="{()=> modalActivate = true}">settings</Icon>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"NGauss_fit"})}">Fit</button>
            <Textfield style="{style}; margin-bottom: 0.5em; margin-left: 1em; margin-right: 1em;" bind:value={savePeakfilename} label="savefile"/>
            <button class="button is-link" on:click="{()=>savefile({file:$felixPeakTable, name:savePeakfilename})}">Save peaks</button>
            <button class="button is-link" on:click="{loadpeakTable}">Load peaks</button>

            <button class="button is-danger" on:click="{()=>{$felixPlotAnnotations=[]; $felixPeakTable=[];NGauss_fit_args={}; window.Plotly.relayout($graphDiv, { annotations: [] }); window.createToast("Cleared", "warning")}}">Clear</button>

        </div>

    </div>
    
{/if}