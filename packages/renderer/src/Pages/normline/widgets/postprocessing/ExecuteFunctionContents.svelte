
<script>
    import { 
        felixIndex, 
        normMethod,
        graphDiv,
        dataTable,
        Ngauss_sigma,
        expfittedLines,
        felixPeakTable,
        felixOutputName,
        felixopoLocation,
        felixPlotAnnotations,
        felixAnnotationColor,
        expfittedLinesCollectedData,
    }                                   from "../../functions/svelteWritables";
    import Textfield                    from '@smui/textfield';
    import CustomSwitch                 from '$components/CustomSwitch.svelte';
    import {savefile, loadfile}         from "../../functions/misc";
    import { fade }                     from 'svelte/transition';
    import {NGauss_fit_func}            from '../../functions/NGauss_fit';
    import {find_peaks_func}            from '../../functions/find_peaks';
    import {exp_fit_func}               from '../../functions/exp_fit';
    import {get_err_func}               from '../../functions/get_err';
    import {relayout, deleteTraces}     from 'plotly.js/dist/plotly-basic';
    import {
        dropRight, uniqBy, 
        filter, sortBy
    }                                   from "lodash-es"
    import computePy_func               from "$src/Pages/general/computePy"

    export let writeFile
    export let fullfiles
    // export let normMethod
    export let addedFileCol
    export let writeFileName
    export let addedFileScale
    export let overwrite_expfit
    export let modalActivate=false
    export let adjustPeakTrigger=false;
    
    let boxSelected_peakfinder=false
    let NGauss_fit_args={}

    let peak_height = 1
    let peak_width = 3
    let peak_prominence = 0;
    let toggleFindPeaksRow = false
    let savePeakfilename = "peakTable";

    const clearAllPeak = () => {

        const graphElement = document.getElementById($graphDiv)
        const noOfFittedData = graphElement.data?.length - fullfiles.length
        if (noOfFittedData === 0) {return window.createToast("No fitted lines found", "danger")}

        console.log("Removing all found peak values")
        console.log({noOfFittedData}, fullfiles.length, graphElement.data?.length)
        $felixIndex = []
        $expfittedLines = []
        $felixPlotAnnotations = []
        $expfittedLinesCollectedData = []
        relayout($graphDiv, { annotations: [], shapes: [] })
        for (let i=0; i<noOfFittedData; i++) {deleteTraces($graphDiv, [-1])}

    }

    const clearLastPeak = () => {
        
        const graphElement = document.getElementById($graphDiv)
        const noOfFittedData = graphElement.data?.length - fullfiles.length
        if (noOfFittedData === 0) {return window.createToast("No fitted lines found", "danger")}
        
        
        plotData({filetype:"general", general:{args:[$felixOutputName, $felixopoLocation, $normMethod], pyfile:"delete_fileLines"}})

        $dataTable = dropRight($dataTable, 1)
        $expfittedLines = dropRight($expfittedLines, 2)
        $felixPlotAnnotations = dropRight($felixPlotAnnotations, 1)
        $expfittedLinesCollectedData = dropRight($expfittedLinesCollectedData, 1)
        relayout($graphDiv, { annotations: $felixPlotAnnotations, shapes: $expfittedLines })

        deleteTraces($graphDiv, [-1])
        console.log("Last fitted peak removed")

    }

    function loadpeakTable(){
        const loadedfile = loadfile(savePeakfilename)
        if(!loadedfile) return
        $felixPeakTable = sortBy(loadedfile, [(o)=>o["freq"]])
        adjustPeak()
    }

    function adjustPeak() {
        const annotationDefaults = {
            xref:"x", y:"y", "showarrow":true,
            arrowhead: 2, ax: -25, ay: -40,
            font: {color: $felixAnnotationColor},
            arrowcolor: $felixAnnotationColor
        }
        
        $felixPlotAnnotations = $felixPeakTable.map((f)=>{
            const {freq, amp} = f
            const x = parseFloat(freq)
            const y = parseFloat(amp)
            const annotate = {x, y, text:`(${x.toFixed(2)}, ${y.toFixed(2)})`}
            return {...annotationDefaults, ...annotate}
        })

        modalActivate = false
        relayout($graphDiv, { annotations: $felixPlotAnnotations })
        adjustPeakTrigger = false
    };

    function plotData({e=null, filetype="exp_fit", general={}}={}){

        if (filetype == "general") {
            const {pyfile, args} = general

            computePy_func({pyfile, args, general:true})
            
            return;
        
        }

        let pyfile="", args;
        let expfit_args = [], find_peaks_args = {}
        
        switch (filetype) {

            case "exp_fit":
                if ($felixIndex.length<2) { return window.createToast("Range not found!!. Select a range using Box-select", "danger") }

                expfit_args = { addedFileScale, addedFileCol, output_name:$felixOutputName, overwrite_expfit, writeFile, writeFileName, normMethod: $normMethod, index:$felixIndex, fullfiles, location:$felixopoLocation }

                pyfile="exp_gauss_fit" , args=[JSON.stringify(expfit_args)]
                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    exp_fit_func({dataFromPython})
                    window.createToast("Line fitted with gaussian function", "success")
                })

                break;

            case "NGauss_fit":

                if (boxSelected_peakfinder) {
                    if ($felixIndex.length<2) { return window.createToast("Box selection is turned ON so please select a wn. range to fit", "danger") }
                    NGauss_fit_args.index = $felixIndex

                } else {delete NGauss_fit_args.index}


                
                if ($felixPeakTable.length === 0) {return window.createToast("No arguments initialised yet.", "danger") }
                
                NGauss_fit_args.fitNGauss_arguments = {}
                $felixPeakTable.forEach((f, index)=>{
                    NGauss_fit_args.fitNGauss_arguments[`cen${index}`] = f.freq
                    NGauss_fit_args.fitNGauss_arguments[`A${index}`] = f.amp
                    NGauss_fit_args.fitNGauss_arguments[`sigma${index}`] = f.sig
                })

                NGauss_fit_args = {...NGauss_fit_args, location:$felixopoLocation, addedFileScale, addedFileCol, overwrite_expfit, writeFile, writeFileName, output_name:$felixOutputName, fullfiles, normMethod: $normMethod}
                pyfile="multiGauss" , args=[JSON.stringify(NGauss_fit_args)]

                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    NGauss_fit_func({dataFromPython})
                    console.log("Line fitted")
                    window.createToast(`Line fitted with ${dataFromPython["fitted_parameter"].length} gaussian function`, "success")
                })
                break;
            
            case "find_peaks":
                
                $felixPeakTable = []

                if ($felixIndex.length<2 && boxSelected_peakfinder) { return window.createToast("Box selection is turned ON so please select a wn. range to fit", "danger") }
                
                const selectedIndex = boxSelected_peakfinder ? $felixIndex : [0, 0]
                find_peaks_args = { addedFileScale, addedFileCol, output_name:$felixOutputName, normMethod: $normMethod, peak_prominence, peak_width, peak_height, selectedIndex, fullfiles, location:$felixopoLocation }



                pyfile="fit_all" ,  args=[JSON.stringify(find_peaks_args)]

                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    find_peaks_func({dataFromPython})
                    console.log(`felixPeakTable:`, $felixPeakTable)
                    window.createToast("Peaks found", "success")
                })

                break;

            case "get_err":
                if ($expfittedLinesCollectedData.length<2) return window.createToast("Not sufficient lines collected!", "danger")
                pyfile="weighted_error" , args=$expfittedLinesCollectedData
                computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    get_err_func({dataFromPython})
                    window.createToast("Weighted fit. done", "success")
                })
                break;

         
            default:
                break;
        }
    }
    $: if(adjustPeakTrigger) adjustPeak()
</script>

<div class="align">
    <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"exp_fit"})}">Exp Fit.</button>
    <button class="button is-link" on:click="{()=>toggleFindPeaksRow = !toggleFindPeaksRow}">Fit NGauss.</button>
    <button class="button is-warning" on:click={clearLastPeak}>Clear Last</button>
    <button class="button is-danger" on:click={clearAllPeak}>Clear All</button>
    <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"get_err"})}">Weighted Mean</button>
    <button class="button is-warning" on:click="{()=>{$expfittedLinesCollectedData = []; window.createToast("Line collection restted", "warning")}}">Reset</button>
</div>

{#if toggleFindPeaksRow}
    <div class="align" transition:fade>

        <div class="align">
        
            <CustomSwitch bind:selected={boxSelected_peakfinder} label="BoxSelected"/>
            <Textfield style="width: 7em;" type="number" step="0.5" bind:value={peak_prominence} label="Prominance" />
            <Textfield style="width: 7em;" type="number" step="0.5" bind:value={peak_width} label="Width" />
            <Textfield style="width: 7em;" type="number" step="0.1" bind:value={peak_height} label="Height" />
            <Textfield style="width: 7em;" bind:value={$Ngauss_sigma} label="Sigma"/>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"find_peaks"})}">Get Peaks</button>
        
        </div>
        
        <div class="align" style="align-items: baseline;">
            <i class="material-icons" on:click="{()=> modalActivate = true}">settings</i>
            <button style="width:7em" class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"NGauss_fit"})}">Fit</button>
            <Textfield bind:value={savePeakfilename} label="savefile"/>
            <button class="button is-link" on:click="{()=>savefile({file:$felixPeakTable, name:savePeakfilename})}">Save peaks</button>
            <button class="button is-link" on:click="{loadpeakTable}">Load peaks</button>
            <button class="button is-danger" on:click="{()=>{$felixPlotAnnotations=[]; $felixPeakTable=[];NGauss_fit_args={}; relayout($graphDiv, { annotations: [] }); window.createToast("Cleared", "warning")}}">Clear</button>
        </div>

    </div>
    
{/if}
