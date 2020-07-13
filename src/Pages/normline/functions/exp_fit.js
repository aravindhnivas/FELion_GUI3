
import {dataTable, dataTable_avg, felixPlotAnnotations} from './svelteWritables';
import { get} from 'svelte/store';
export function exp_fit_func({dataFromPython, graphDiv, output_name, line, plot_trace_added, line_index_count, collectData, lineData_list}={}){

    Plotly.addTraces(graphDiv, dataFromPython["fit"])
    line = [...line, ...dataFromPython["line"]]

    Plotly.relayout(graphDiv, { shapes: line })

    let annotations = dataFromPython["annotations"]
    felixPlotAnnotations.update(annotate => [...annotate, annotations])

    Plotly.relayout(graphDiv, { annotations: get(felixPlotAnnotations) })
    
    plot_trace_added++

    let [freq, amp, fwhm, sig] = dataFromPython["table"].split(", ")
    
    let color = "#fafafa";
    
    if (output_name === "averaged") {

        color = "#836ac05c"
        dataTable_avg.update(table=>[...table, {name: `Line #${line_index_count}`, id:getID(), freq, amp, fwhm, sig, color}])
        dataTable_avg.update(table=>_.uniqBy(table, "freq"))
        
        line_index_count++
    } else {
        
        if (collectData) {
            console.log("Collecting lines")
            lineData_list = [...lineData_list, dataFromPython["for_weighted_error"]]
            }
    }
    let newTable = {name: output_name, id:getID(), freq, amp, fwhm, sig, color}
    dataTable.update(table=>_.uniqBy([...table, newTable], "freq"))
    console.log("Line fitted")

    return [line, plot_trace_added, line_index_count, collectData, lineData_list]

}