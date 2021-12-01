
import { plotlyEventCreatedFELIX, get } from './svelteWritables';
import { subplot } from "../../../js/functions.js";
import { plotlySelection, plotlyClick } from "./misc";
import beforePlot from "./beforePlot";

export async function felix_func({ dataFromPython, delta } = {}) {

    await beforePlot({ delta, dataFromPython, graphDiv: "avgplot", baseGraphDiv:"bplot" })

    subplot(
        "Spectrum and Power Analyser",

        "Wavelength set (cm-1)",
        "SA (cm-1)",
        dataFromPython["SA"],

        "saPlot",

        "Wavelength (cm-1)",
        `Total Power (mJ)`,
        dataFromPython["pow"]
    );

    if (!get(plotlyEventCreatedFELIX)) {
        const plot = { graphDiv: "avgplot", mode: "felix" }
        plotlySelection(plot), plotlyClick(plot);

        plotlyEventCreatedFELIX.set(true)

    }

    const graphDivIds = ["exp-theory-plot", "bplot", "saPlot", "avgplot", "opoplot", "opoSA", "opoRelPlot"]
    graphDivIds.forEach(id=>{

        const content = document.getElementById(id).innerHTML
        
        const width = document.getElementById(id).clientWidth
        
        if(content){ window.Plotly.relayout(id, {width}) }
    })



    console.log("Graph Plotted")

}