
<script>
    import {
        showall,
        felixIndex, 
        normMethod,
        graphDiv,
        dataTable,
        expfittedLines,
        felixPeakTable,
        felixOutputName,
        felixopoLocation,
        felixPlotAnnotations,
        felixAnnotationColor,
        expfittedLinesCollectedData,
    }                                   from "../../functions/svelteWritables";
    import Textfield                    from '@smui/textfield';
    import {savefile, loadfile}         from "../../functions/misc";
    import { fade }                     from 'svelte/transition';
    import {NGauss_fit_func}            from '../../functions/NGauss_fit';
    import {exp_fit_func}               from '../../functions/exp_fit';
    import {relayout, deleteTraces}     from 'plotly.js/dist/plotly-basic';
    import {dropRight, sortBy}          from "lodash-es"
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
        relayout($graphDiv, { annotations: [], shapes: [], line: [] })
        const defaultLength = $showall ? fullfiles.length : 1
        const noOfFittedData = graphElement.data?.length - defaultLength
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
        const defaultLength = $showall ? fullfiles.length : 1
        const noOfFittedData = graphElement.data?.length - defaultLength
        if (noOfFittedData === 0) {return window.createToast("No fitted lines found", "danger")}
        $dataTable = dropRight($dataTable, 1)
        $expfittedLines = dropRight($expfittedLines, 2)
        
        $felixPlotAnnotations = dropRight($felixPlotAnnotations, 1)
        $expfittedLinesCollectedData = dropRight($expfittedLinesCollectedData, 1)
        relayout($graphDiv, { annotations: $felixPlotAnnotations, shapes: $expfittedLines })

        deleteTraces($graphDiv, [-1])
        window.createToast("Last fitted peak removed", "warning")

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

        switch (filetype) {

            case "exp_fit":
                if ($felixIndex.length<2) { return window.createToast("Range not found!!. Select a range using Box-select", "danger") }

                const expfit_args = { 
                    fullfiles,
                    writeFile,
                    addedFileCol,
                    writeFileName,
                    addedFileScale,
                    overwrite_expfit,
                    normMethod: $normMethod,
                    index: $felixIndex,
                    location: $felixopoLocation,
                    output_name:$felixOutputName,
                }
                computePy_func({e, pyfile: "normline.exp_gauss_fit", args: JSON.stringify(expfit_args)})
                .then((dataFromPython)=>{
                    exp_fit_func({dataFromPython})
                    window.createToast("Line fitted with gaussian function", "success")
                })
                
                break;

            case "NGauss_fit":

                if (boxSelected_peakfinder) {
                    if ($felixIndex.length<2) { 
                        window.createToast(
                            "Box selection is turned ON so please select a wn. range to fit", 
                            "danger"
                        )
                        return
                    }
                    NGauss_fit_args.index = $felixIndex
                } else {NGauss_fit_args.index = []}

                if ($felixPeakTable.length === 0) {
                    return window.createToast("No arguments initialised yet.", "danger") 

                }
                
                
                NGauss_fit_args.fitNGauss_arguments = {}


                $felixPeakTable.forEach((f, index)=>{
                    NGauss_fit_args.fitNGauss_arguments[`cen${index}`] = f.freq
                    NGauss_fit_args.fitNGauss_arguments[`A${index}`] = f.amp
                    NGauss_fit_args.fitNGauss_arguments[`sigma${index}`] = f.sig
                })
                NGauss_fit_args = {
                    ...NGauss_fit_args, location: $felixopoLocation, addedFileScale, addedFileCol, overwrite_expfit, writeFile, writeFileName, output_name: $felixOutputName, fullfiles, normMethod: $normMethod
                }

                computePy_func({e, pyfile: "normline.multiGauss" , args: JSON.stringify(NGauss_fit_args)})
                .then((dataFromPython)=>{
                    NGauss_fit_func({dataFromPython})
                    console.log("Line fitted")
                    window.createToast(`Line fitted with ${dataFromPython["fitted_parameter"].length} gaussian function`, "success")
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
</div>

{#if toggleFindPeaksRow}
    <div class="align v-baseline">

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
