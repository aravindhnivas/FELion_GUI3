
import {dataTable, dataTable_avg} from './svelteWritables';

export function NGauss_fit_func({graphDiv, dataFromPython, output_name, line_index_count}={}){

    Plotly.addTraces(graphDiv, dataFromPython["fitted_data"])
    let color = "#fafafa";
    
    dataFromPython["fitted_parameter"].forEach(data=>{
        let {freq, amp, fwhm, sig} = data
    
        if (output_name === "averaged") {
            
            color = "#836ac05c"
            
            dataTable_avg.update(table =>  [...table, {name: `Line #${line_index_count}`, id:getID(), freq:freq, amp:amp, fwhm:fwhm, sig:sig, color:color}])

            dataTable_avg.update(table => _.uniqBy(table, "freq"))
    
            line_index_count++
        }
        let newTable = {name: output_name, id:getID(), freq:freq, amp:amp, fwhm:fwhm, sig:sig, color:color}
        
        dataTable.update(table =>  _.uniqBy([...table, newTable], "freq"))
    })

    return line_index_count
    
}