import {felixIndex, felixOutputName, opoMode} from './svelteWritables';
import {plot} from "../../../js/functions.js";

export function opofile_func({dataFromPython, plotly_event_created_opo}={}) {

    felixOutputName.set("averaged")
    
    
    plot("OPO spectrum", "Wavenumber (cm-1)", "Counts", dataFromPython["real"], "opoplot")
    plot("OPO Calibration", "Set Wavenumber (cm-1)", "Measured Wavenumber (cm-1)", dataFromPython["SA"], "opoSA")
    plot("OPO spectrum: Depletion (%)", "Wavenumber (cm-1)", "Depletion (%)", dataFromPython["relative"], "opoRelPlot")
    let opoRelPlot = document.getElementById("opoRelPlot")

    if(!plotly_event_created_opo){

        console.log("Creating plotly graph events")

        opoRelPlot.on("plotly_selected", (data) => {

            if (!data) console.log("No data available to fit")
            else {
                console.log(data)
                opoMode.set(true)
                let { range } = data
                let output_name = data.points[0].data.name.split(".")[0]
                index = range.x
                
                felixOutputName.set(output_name)
                felixIndex.set(index)
                console.log(`Selected file: ${output_name}`)
                console.log(`Index selected: ${index}`)
            }
        })
        plotly_event_created_opo = true
    }

    console.log("Graph Plotted")

    
    return plotly_event_created_opo
}