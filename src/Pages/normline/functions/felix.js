
import {felixIndex, felixOutputName, opoMode, normMethodDatas, plotlyEventCreatedFELIX, get} from './svelteWritables';
import {plot, subplot} from "../../../js/functions.js";
import {plotlySelection, plotlyClick} from "./misc";

export function felix_func({normMethod, dataFromPython, delta}={}){
    opoMode.set(false), felixOutputName.set("averaged"), felixIndex.set([])
    
    let avgdataToPlot, signal_formula, ylabel;
    
    if (normMethod === "Log") {
        avgdataToPlot = dataFromPython["average"]
        signal_formula = "Signal = -ln(C/B)/Power(in J)"
        ylabel = "Normalised Intensity per J"
    } else if (normMethod == "Relative") {
        avgdataToPlot = dataFromPython["average_rel"]
        signal_formula = "Signal = (1-C/B)*100"
        ylabel = "Relative Depletion (%)"

    } else if (normMethod == "IntensityPerPhoton") {

        avgdataToPlot = dataFromPython["average_per_photon"]

        signal_formula = "Signal = -ln(C/B)/#Photons"
        ylabel = "Normalised Intensity per photon"
    }
    const get_data = (data) => {
        let dataPlot = [];
        for (let x in data) { dataPlot.push(data[x]) }
        return dataPlot
    }
    let signal = {
        "rel": "Signal = (1-C/B)*100", "log": "Signal = -ln(C/B)/Power(in J)",
        "hv": "Signal = -ln(C/B)/#Photons"
    }


    const set_title = (method) => `Normalised and Averaged Spectrum (delta=${delta})<br>${signal[method]}; {C=Measured Count, B=Baseline Count}`

    const normMethod_datas = {
        "Relative": {
            "data": get_data(dataFromPython["average_rel"]),
            "layout": {
                "title": set_title("rel"),
                "yaxis": { "title": "Relative Depletion (%)" },
                "xaxis": { "title": "Calibrated Wavelength (cm-1)" }
            }
        },
        "Log": {
            "data": get_data(dataFromPython["average"]),
            "layout": {
                "title": set_title("log"),
                "yaxis": { "title": "Normalised Intensity per J" },
                "xaxis": { "title": "Calibrated Wavelength (cm-1)" }
            }
        },
        "IntensityPerPhoton": {
            "data": get_data(dataFromPython["average_per_photon"]),
            "layout": {
                "title": set_title("hv"),
                "yaxis": { "title": "Normalised Intensity per photon" },
                "xaxis": { "title": "Calibrated Wavelength (cm-1)" }
            }
        },

    }

    normMethodDatas.set(normMethod_datas)

    plot(
        "Baseline Corrected",
        "Wavelength (cm-1)",
        "Counts",
        dataFromPython["base"],
        "bplot"
    );

    plot(
        `Normalised and Averaged Spectrum (delta=${delta})<br>${signal_formula}; {C=Measured Count, B=Baseline Count}`,
        "Calibrated Wavelength (cm-1)",
        ylabel,
        avgdataToPlot,
        "avgplot"
    );


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

    
    if(!get(plotlyEventCreatedFELIX)){
        const plot = {graphDiv:"avgplot", mode:"felix"}
        plotlySelection(plot), plotlyClick(plot);

        plotlyEventCreatedFELIX.set(true)

    }
    console.log("Graph Plotted")

}


