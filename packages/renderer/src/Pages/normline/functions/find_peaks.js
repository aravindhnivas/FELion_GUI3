
import {felixPeakTable, Ngauss_sigma, felixPlotAnnotations, graphDiv, felixAnnotationColor, get} from "./svelteWritables";

export function find_peaks_func({dataFromPython}={}){

    const annotations = dataFromPython[2]["annotations"]

    felixPlotAnnotations.set(annotations)

    const color = annotations["arrowcolor"]
    felixAnnotationColor.set(color)
    window.Plotly.relayout(get(graphDiv), { annotations  })

    const [peakX, peakY] = [dataFromPython[0]["data"].x, dataFromPython[0]["data"].y]
    for (let index = 0; index < peakX.length; index++) {
        let [freq, amp, sig] = [peakX[index], peakY[index], get(Ngauss_sigma)]

        felixPeakTable.update(table => [...table, {freq, amp, sig, id:getID()}])

    }
    console.log(`Found peaks:\nX: ${peakX}\nY: ${peakY}`)
    console.log("Peaks found")
}