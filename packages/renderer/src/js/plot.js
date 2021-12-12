
import {react} from 'plotly.js/dist/plotly';
export function plot(mainTitle, xtitle, ytitle, data, plotArea, logScale=null) {

    let dataLayout = {
        title: mainTitle,
        xaxis: { title: xtitle },
        yaxis: { title: ytitle , type: logScale},
        hovermode: 'closest',

        autosize: true,
        height: 450,
    }

    // if (filetype == 'mass') { dataLayout.yaxis.type = "log" }

    let dataPlot = [];

    for (let x in data) { dataPlot.push(data[x]) }

    try { react(plotArea, dataPlot, dataLayout, { editable: true }) } catch (err) { console.log("Error occured while plotting\n", err) }
}

export function subplot(mainTitle, xtitle, ytitle, data, plotArea, x2, y2, data2) {

    let dataLayout = {
        title: mainTitle,
        xaxis: { domain: [0, 0.4], title: xtitle },
        yaxis: { title: ytitle },
        xaxis2: { domain: [0.5, 1], title: x2 },
        yaxis2: { anchor: "x2", title: y2, overlaying: 'y', },

        yaxis3: { anchor: 'free', overlaying: 'y', side: 'right', title: "Measured (mJ)", position: 0.97 },
        autosize: true,
        height: 450,

    }
    let dataPlot1 = [];

    for (let x in data) { dataPlot1.push(data[x]) }

    let dataPlot2 = [];
    for (let x in data2) { dataPlot2.push(data2[x]) }

    react(plotArea, dataPlot1.concat(dataPlot2), dataLayout, { editable: true })

}