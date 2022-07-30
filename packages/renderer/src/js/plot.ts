import { activePage } from '$src/sveltewritables'
import { react, relayout } from 'plotly.js-basic-dist'
import { find, differenceBy } from 'lodash-es'
import { writable, get } from 'svelte/store'

export const graph_detached = writable<{ [name: string]: boolean }>({})
interface PlotlyEventsInfo {
    [name: string]: {
        eventCreated: boolean
        annotations: Partial<Plotly.Annotations>[]
    }
}

export const graphPlottedLists: {
    [key: string]: boolean
} = {}

export const plotlyEventsInfo= writable<PlotlyEventsInfo>({})

export function plot(
    mainTitle: string, 
    xtitle: string, 
    ytitle: string,
    data: DataFromPython, 
    graphDiv: string,
    logScale: boolean = false, 
    createPlotlyClickEvent = false
) {
    
    // const graph_div = document.getElementById(graphDiv)
    const current_graph_detached = get(graph_detached)[get(activePage)]

    const graph_container = document.querySelector(
        current_graph_detached 
            ? `#${graphDiv}` 
            : `#${get(activePage)} .plot__div`
    ) as HTMLDivElement
    
    const pad = graphPlottedLists[get(activePage)] ? 16 : 32
    const width = graph_container?.clientWidth - (current_graph_detached ? 0 : pad)

    const dataLayout: Partial<Plotly.Layout> = {
        title: mainTitle,
        xaxis: { title: xtitle },
        yaxis: { title: ytitle, type: logScale ? 'log' : 'linear' },
        hovermode: 'closest',
        autosize: true,
        height: 450,
        width: width,
    }

    const dataPlot: PlotData[] = []
    
    for (const x in data) {
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
        if (graphPlottedLists[get(activePage)]) return

        graphPlottedLists[get(activePage)] = true

    } catch (error) {
        console.error('Error occured while plotting\n', error)
        window.handleError(error)
    }
}

export function subplot(
    mainTitle: string, 
    xtitle: string, 
    ytitle: string, 
    data: DataFromPython, 
    graphDiv: string, 
    x2: string, 
    y2: string, 
    data2: DataFromPython
) {

    const current_graph_detached = get(graph_detached)[get(activePage)]

    const graph_container = document.querySelector(
        current_graph_detached 
            ? `#${graphDiv}` 
            : `#${get(activePage)} .plot__div`
    ) as HTMLDivElement
    
    const pad = graphPlottedLists[get(activePage)] ? 16 : 32
    const width = graph_container?.clientWidth - (current_graph_detached ? 0 : pad)

    const dataLayout: Partial<Plotly.Layout>  = {
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
        width: width
    }

    const dataPlot1: PlotData[] = []
    for (const x in data) {
        dataPlot1.push(data[x])
    }

    const dataPlot2: PlotData[] = []
    for (const x in data2) {
        dataPlot2.push(data2[x])
    }

    react(graphDiv, dataPlot1.concat(dataPlot2), dataLayout, { editable: true })
}

export function plotlyClick(graphDiv: string): boolean {

    const graph = document.getElementById(graphDiv) as Plotly.PlotlyHTMLElement & {layout: Plotly.Layout}
    plotlyEventsInfo.update((info) => {
        const contents = info[graphDiv]
        contents.annotations = []
        return { ...info, contents }
    })

    graph.on('plotly_click', (data) => {
        if (data.event.ctrlKey) {
            const { points } = data

            const currentDataPoint = points[0]
            console.log(currentDataPoint)
            
            const { x: mass, y: counts } = currentDataPoint as {x: number, y: number }

            if (data.event.shiftKey) {
                const annotate = find(get(plotlyEventsInfo)[graphDiv].annotations, (m) => {
                    return <number>m.x >= mass - 0.2 && <number>m.x <= mass + 0.2
                })

                const annotations = differenceBy(get(plotlyEventsInfo)[graphDiv].annotations, [annotate], 'x')
                plotlyEventsInfo.update((info) => {
                    const contents = info[graphDiv]
                    contents.annotations = annotations
                    return { ...info, contents }
                })

                console.log(get(plotlyEventsInfo)[graphDiv].annotations, annotate)

            } else {
                
                const logScale = graph?.layout.yaxis.type === 'log'
                
                // @ts-ignore
                const { color } = currentDataPoint.fullData.line || currentDataPoint.fullData.marker || ''

                const annotate: Partial<Plotly.Annotations> = {
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
