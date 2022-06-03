import { react, relayout } from 'plotly.js/dist/plotly-basic'
import { find, differenceBy } from 'lodash-es'
import { writable, get } from 'svelte/store'
import type { Writable } from 'svelte/store'

type PlotlyEventsInfo = {
    [name: string]: {
        eventCreated: boolean
        annotations: Plotly.Annotations[]
    }
}
export const plotlyEventsInfo: Writable<PlotlyEventsInfo> = writable({})

export function plot(mainTitle: string, xtitle: string, ytitle: string, data: {[name: string]: Plotly.PlotData}, graphDiv: string, logScale:boolean = null, createPlotlyClickEvent = false) {
    let dataLayout = {
        title: mainTitle,
        xaxis: { title: xtitle },
        yaxis: { title: ytitle, type: logScale },
        hovermode: 'closest',
        autosize: true,
        height: 450,
    }

    let dataPlot: Plotly.PlotData[] = []
    for (let x in data) {
        dataPlot.push(data[x])
    }

    try {
        react(graphDiv, dataPlot, dataLayout, { editable: true })
        if (!get(plotlyEventsInfo)[graphDiv]) {
            get(plotlyEventsInfo)[graphDiv] = {
                eventCreated: false,
                annotations: []
            }
        }
        console.log(graphDiv, ': plotted', get(plotlyEventsInfo)[graphDiv].eventCreated)
        if (!get(plotlyEventsInfo)[graphDiv].eventCreated && createPlotlyClickEvent) {
            console.log('Creating plotly event for ', graphDiv)
            plotlyClick(graphDiv)
        }
    } catch (err) {
        console.error('Error occured while plotting\n', err)
        window.handleError(err)
    }
}

export function subplot(mainTitle, xtitle, ytitle, data, graphDiv, x2, y2, data2) {
    let dataLayout = {
        title: mainTitle,
        xaxis: { domain: [0, 0.4], title: xtitle },
        yaxis: { title: ytitle },
        xaxis2: { domain: [0.5, 1], title: x2 },
        yaxis2: { anchor: 'x2', title: y2, overlaying: 'y' },

        yaxis3: {
            anchor: 'free',
            overlaying: 'y',
            side: 'right',
            title: 'Measured (mJ)',
            position: 0.97,
        },
        autosize: true,
        height: 450,
    }
    let dataPlot1 = []

    for (let x in data) {
        dataPlot1.push(data[x])
    }

    let dataPlot2 = []
    for (let x in data2) {
        dataPlot2.push(data2[x])
    }

    react(graphDiv, dataPlot1.concat(dataPlot2), dataLayout, { editable: true })
}

export function plotlyClick(graphDiv: string): boolean {

    const graph = document.getElementById(graphDiv) as Plotly.PlotlyHTMLElement
    plotlyEventsInfo.update((info) => {
        const contents = info[graphDiv]
        contents.annotations = []
        return { ...info, contents }
    })

    graph.on('plotly_click', (data) => {
        if (data.event.ctrlKey) {
            const { points } = data
            const currentDataPoint = points[0]
            const { x: mass, y: counts } = currentDataPoint

            // console.log(currentDataPoint)
            if (data.event.shiftKey) {
                const annotate = find(get(plotlyEventsInfo)[graphDiv].annotations, (m) => {
                    return m.x >= <number>mass - 0.2 && m.x <= <number>mass + 0.2
                })

                const annotations = differenceBy(get(plotlyEventsInfo)[graphDiv].annotations, [annotate], 'x')
                plotlyEventsInfo.update((info) => {
                    const contents = info[graphDiv]
                    contents.annotations = annotations
                    return { ...info, contents }
                })

                console.log(get(plotlyEventsInfo)[graphDiv].annotations, annotate)

            } else {

                let logScale = graph?.layout.yaxis.type === 'log'
                const { color } = currentDataPoint.fullData.line || currentDataPoint.fullData.marker || ''

                const annotate = {
                    text: `(${mass.toFixed(1)}, ${counts.toFixed(1)})`,
                    x: mass,
                    y: logScale ? Math.log10(counts) : counts,
                    xref: 'x',
                    yref: 'y',
                    font: { color },
                    showarrow: true,
                    arrowhead: 2,
                    arrowcolor: color,
                }

                plotlyEventsInfo.update((info) => {
                    const contents = info[graphDiv]
                    contents.annotations = [...contents.annotations, annotate]
                    return { ...info, contents }
                })
            }
            relayout(graph, {
                annotations: get(plotlyEventsInfo)[graphDiv].annotations,
            })
            console.log({
                graph,
                annotations: get(plotlyEventsInfo)[graphDiv].annotations,
            })
        }
    })

    plotlyEventsInfo.update((info) => {
        const contents = info[graphDiv]

        contents.eventCreated = true
        return { ...info, contents }
    })
    console.log('Plotly event created for ', graphDiv)

    return true
}
