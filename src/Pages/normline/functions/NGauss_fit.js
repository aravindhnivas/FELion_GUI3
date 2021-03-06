
import {dataTable, dataTable_avg, graphDiv, felixOutputName, avgfittedLineCount, fittedTraceCount, get} from './svelteWritables';

export function NGauss_fit_func({dataFromPython}={}) {

    Plotly.addTraces(get(graphDiv), dataFromPython["fitted_data"])
    fittedTraceCount.update(n=>n+1)

    const output_name = get(felixOutputName)
    const color = output_name === "averaged" ? "#836ac05c" : "#fafafa";

    // dataTable

    let newTable = dataFromPython["fitted_parameter"].map((data)=>{
        let {freq, amp, fwhm, sig} = data
        return {name: output_name, id:getID(), freq:freq, amp:amp, fwhm:fwhm, sig:sig, color:color}
    
    })

    dataTable.set(_.uniqBy(newTable, "freq"))

    // dataTable_avg
    if(output_name === "averaged") {
        let newTable =dataFromPython["fitted_parameter"].map((data, index)=>{
            let {freq, amp, fwhm, sig} = data

            return {name: `Line #${index}`, id:getID(), freq:freq, amp:amp, fwhm:fwhm, sig:sig, color:color}

        })
        dataTable_avg.set(_.uniqBy(newTable, "freq"))
        avgfittedLineCount.set(get(dataTable_avg).length)
    }
}