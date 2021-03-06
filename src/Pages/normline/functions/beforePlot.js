
import { felixIndex, felixOutputName, normMethod, opoMode, felixData, opoData, get } from './svelteWritables';
import { plot } from "../../../js/functions.js";

export default function beforePlot({ delta, dataFromPython, graphDiv, baseGraphDiv } = {}) {

    felixOutputName.set("averaged"), felixIndex.set([])

    let avgdataToPlot, signal_formula, ylabel;

    if (get(normMethod) === "Log") {
        avgdataToPlot = dataFromPython["average"]
        signal_formula = "Signal = -ln(C/B)/Power(in J)"
        ylabel = "Normalised Intensity per J"
    } else if (get(normMethod) == "Relative") {
        avgdataToPlot = dataFromPython["average_rel"]
        signal_formula = "Signal = (1-C/B)*100"
        ylabel = "Relative Depletion (%)"

    } else if (get(normMethod) == "IntensityPerPhoton") {

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

        }

    }


    if (get(opoMode)) { opoData.set(normMethod_datas) } else { { felixData.set(normMethod_datas) } }

    plot(
        "Baseline Corrected",
        "Wavelength (cm-1)",

        "Counts",
        dataFromPython["base"], baseGraphDiv
        
    );

    plot(
        `Normalised and Averaged Spectrum (delta=${delta})<br>${signal_formula}; {C=Measured Count, B=Baseline Count}`,
        "Calibrated Wavelength (cm-1)",
        ylabel,
        avgdataToPlot, graphDiv
    );


    return Promise.resolve()

}