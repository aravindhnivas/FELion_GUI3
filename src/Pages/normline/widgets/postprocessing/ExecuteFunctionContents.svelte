

<script>
    import { fittedTraceCount, felixPlotAnnotations, felixIndex, expfittedLines, expfittedLinesCollectedData , graphDiv, dataTable, Ngauss_sigma, felixOutputName, felixPeakTable, felixopoLocation, felixAnnotationColor} from "../../functions/svelteWritables";
    import Textfield from '@smui/textfield';
    import CustomSwitch from '../../../../components/CustomSwitch.svelte';
    import {Icon} from '@smui/icon-button';

    import AdjustInitialGuess from "../../modals/AdjustInitialGuess.svelte";
    import {savefile, loadfile} from "../../functions/misc";
    import {createToast} from "../../../../components/Layout.svelte"
    export let plotData, boxSelected_peakfinder=false, peak_height, peak_width, peak_prominence, NGauss_fit_args;

    let toggleFindPeaksRow = false, savePeakfilename = "peakTable", modalActivate=false;

    const style = "width:7em; height:3.5em; margin-right:0.5em";

    const clearAllPeak = () => {
        if ($fittedTraceCount === 0) {return createToast("No fitted lines found", "danger")}

        console.log("Removing all found peak values")
        
        $felixPlotAnnotations = $felixIndex = $expfittedLines = $expfittedLinesCollectedData = []

        Plotly.relayout($graphDiv, { annotations: [], shapes: [] })
        
        for (let i=0; i<$fittedTraceCount; i++) {Plotly.deleteTraces($graphDiv, [-1])}
        
        $fittedTraceCount = 0
    }

    const clearLastPeak = () => {
        
        if ($fittedTraceCount === 0) {return createToast("No fitted lines found", "danger")}

        plotData({filetype:"general", general:{args:[$felixOutputName, $felixopoLocation], pyfile:"delete_fileLines.py"}})
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
            let _annotate = {x:f.freq, y:f.amp, text:`(${f.freq.toFixed(2)}, ${f.amp.toFixed(2)})`}
            return {...temp_annotate, ..._annotate}
        })

        if(closeMainModal) {
            modalActivate = false, createToast("Initial guess adjusted for full spectrum fitting")
        }
        Plotly.relayout($graphDiv, { annotations:$felixPlotAnnotations })
    };

</script>

<AdjustInitialGuess bind:active={modalActivate} on:save={adjustPeak}/>


<div class="content">
    <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"exp_fit"})}">Exp Fit.</button>
    <button class="button is-link" on:click="{()=>toggleFindPeaksRow = !toggleFindPeaksRow}">Fit NGauss.</button>
    <button class="button is-warning" on:click={clearLastPeak}>Clear Last</button>
    <button class="button is-danger" on:click={clearAllPeak}>Clear All</button>
    <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"get_err"})}">Weighted Mean</button>
    <button class="button is-warning" on:click="{()=>{$expfittedLinesCollectedData = []; createToast("Line collection restted", "warning")}}">Reset</button>

</div>

<!-- Fit peaks functions -->

{#if toggleFindPeaksRow}

    <div class="content" >

        <div style="margin:1em 0">
            <CustomSwitch style="margin: 0 1em;" bind:selected={boxSelected_peakfinder} label="BoxSelected"/>
            <Textfield type="number" {style} step="0.5" bind:value={peak_prominence} label="Prominance" />
            <Textfield type="number" {style} step="0.5" bind:value={peak_width} label="Width" />

            <Textfield type="number" {style} step="0.1" bind:value={peak_height} label="Height" />
            <Textfield style="width:9em" bind:value={$Ngauss_sigma} label="Sigma"/>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"find_peaks"})}">Get Peaks</button>
        </div>
        
        <div style="display:flex; align-items:center">
            <Icon class="material-icons" on:click="{()=> modalActivate = true}">settings</Icon>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"NGauss_fit"})}">Fit</button>
            <Textfield {style} bind:value={savePeakfilename} label="savefile"/>

            <button class="button is-link" on:click="{()=>savefile({file:$felixPeakTable, name:savePeakfilename})}">Save peaks</button>

            <button class="button is-link" on:click="{loadpeakTable}">Load peaks</button>

            <button class="button is-danger" on:click="{()=>{$felixPlotAnnotations=[]; $felixPeakTable=[];NGauss_fit_args={}; window.Plotly.relayout($graphDiv, { annotations: [] }); createToast("Cleared", "warning")}}">Clear</button>
        </div>


    </div>

{/if}