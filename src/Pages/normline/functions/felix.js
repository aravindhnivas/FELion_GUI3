
import {felixIndex, felixPeakTable, felixOutputName, opoMode, normMethodDatas, Ngauss_sigma, felixPlotAnnotations, plotlyEventCreatedFELIX} from './svelteWritables';
import {get} from 'svelte/store';
import {plot, subplot} from "../../../js/functions.js";

let avgplot;
window.addEventListener('DOMContentLoaded', (event) => {

    avgplot = document.getElementById("avgplot");
});


export function felix_func({normMethod, dataFromPython, delta, plotly_event_created}={}){

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

    
    if (!get(plotlyEventCreatedFELIX)) {
        plotlySelection(), plotlyClick();
        plotlyEventCreatedFELIX.set(true)

    }
    console.log("Graph Plotted")

}

function plotlySelection() {

    console.log("Creating plotly graph events")

    avgplot.on("plotly_selected", (data) => {
        if (!data) console.log("No data available to fit")

        else {
        
            console.log(data)
            opoMode.set(false)

            const { range } = data
            felixIndex.set(range.x)

            const output_name = data.points[0].data.name.split(".")[0]
            felixOutputName.set(output_name)

            console.log(`Selected file: ${get(felixOutputName)}`)
        }

    })
}


function plotlyClick(){

    avgplot.on('plotly_click', (data)=>{
        console.log("Graph clicked: ", data)

        if (data.event.ctrlKey) {

            console.log("Data point length: ", data.points.length)
            
            for(let i=0; i<data.points.length; i++){

                console.log("Running cycle: ", i)
                let d = data.points[i]
                let name = d.data.name
                let output_name = get(felixOutputName);

                if (name.includes(output_name)){

                    console.log("Filename: ", output_name)

                    let line_color = d.data.line.color
                    console.log(name)
                    console.log(d, d.x, d.y)

                    let [freq, amp] = [parseFloat(d.x.toFixed(2)), parseFloat(d.y.toFixed(2))]
                    const annotation = { text: `(${freq}, ${amp})`, x: freq, y: amp, font:{color:line_color}, arrowcolor:line_color }
                    felixPlotAnnotations.update(annotate => _.uniqBy([...annotate, annotation], 'text'))
                    Plotly.relayout("avgplot",{annotations: get(felixPlotAnnotations)})

                    felixPeakTable.update(table => [...table, {freq, amp, sig:get(Ngauss_sigma), id:getID()}])
                    felixPeakTable.update(table => _.uniqBy(table, 'freq'))
                }
            }

            console.log("Running cycle ended")
        } 
    })

}