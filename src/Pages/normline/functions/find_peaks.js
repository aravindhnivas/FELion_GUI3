
import {felixPeakTable} from "./svelteWritables"

export function find_peaks_func({graphDiv, dataFromPython, annotation_color, Ngauss_sigma}={}){

    Plotly.relayout(graphDiv, { annotations: [] })
        
    
        window.annotation = dataFromPython[2]["annotations"]

        annotation_color = dataFromPython[2]["annotations"]["arrowcolor"]
        Plotly.relayout(graphDiv, { annotations: dataFromPython[2]["annotations"] })

        const [peakX, peakY] = [dataFromPython[0]["data"].x, dataFromPython[0]["data"].y]
        for (let index = 0; index < peakX.length; index++) {
            let [freq, amp, sig] = [peakX[index], peakY[index], Ngauss_sigma]

            felixPeakTable.update(table => [...table, {freq, amp, sig, id:getID()}])
        }

        console.log(`Found peaks:\nX: ${peakX}\nY: ${peakY}`)
        console.log("Peaks found")
        return annotation_color
}