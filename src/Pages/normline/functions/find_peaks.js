
import {felixPeakTable, Ngauss_sigma, felixPlotAnnotations} from "./svelteWritables";
import { get} from 'svelte/store';
export function find_peaks_func({graphDiv, dataFromPython, annotation_color}={}){

    const annotations = dataFromPython[2]["annotations"]    
    felixPlotAnnotations.set(annotations)

    annotation_color = annotations["arrowcolor"]
    Plotly.relayout(graphDiv, { annotations  })

    const [peakX, peakY] = [dataFromPython[0]["data"].x, dataFromPython[0]["data"].y]
    for (let index = 0; index < peakX.length; index++) {
        let [freq, amp, sig] = [peakX[index], peakY[index], get(Ngauss_sigma)]

        felixPeakTable.update(table => [...table, {freq, amp, sig, id:getID()}])

    }
    console.log(`Found peaks:\nX: ${peakX}\nY: ${peakY}`)
    console.log("Peaks found")
    return annotation_color
}