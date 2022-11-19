import {
    get,
    opoMode,
    dataTable,
    dataTable_avg,
    frequencyDatas,
    expfittedLines,
    felixOutputName,
    fittedTraceCount,
    avgfittedLineCount,
    felixPlotAnnotations,
    expfittedLinesCollectedData,
} from './svelteWritables'
import { relayout, addTraces } from 'plotly.js-basic-dist'
import { uniqBy } from 'lodash-es'

export function exp_fit_func({ dataFromPython, uniqueID }) {
    const currentGraph = get(opoMode) ? `${uniqueID}-opoRelPlot` : `${uniqueID}-avgplot`
    addTraces(currentGraph, dataFromPython['fit'])
    fittedTraceCount.update((n) => n + 1)

    expfittedLines.update((lines) => [...lines, ...dataFromPython['line']])
    relayout(currentGraph, { shapes: get(expfittedLines) })

    const annotations = dataFromPython['annotations']

    felixPlotAnnotations.update((data) => {
        data[uniqueID] = uniqBy([...data[uniqueID], annotations], 'text')
        return data
    })
    relayout(currentGraph, { annotations: get(felixPlotAnnotations)[uniqueID] })

    let [freq, amp, fwhm, sig] = dataFromPython['table'].split(', ')

    let color = '#fafafa'

    const output_name = felixOutputName.get(uniqueID) as string
    if (output_name === 'averaged') {
        color = '#836ac05c'

        const newTable = {
            name: `Line #${get(avgfittedLineCount)}`,
            id: window.getID(),
            freq,
            amp,
            fwhm,
            sig,
            color,
        }
        dataTable_avg.update((data) => {
            data[uniqueID] = uniqBy([...data[uniqueID], newTable], 'freq')
            return data
        })
        avgfittedLineCount.update((n) => n + 1)
    }
    let newTable = {
        name: output_name,
        id: window.getID(),
        freq,
        amp,
        fwhm,
        sig,
        color,
    }

    // dataTable.update((table) => uniqBy([...table, newTable], 'freq'))
    // console.warn(dataTable.get())
    dataTable.update((data) => {
        data[uniqueID] = uniqBy([...data[uniqueID], newTable], 'freq')
        return data
    })
    console.warn(frequencyDatas.get())
    frequencyDatas.update((data) => {
        data[uniqueID] = uniqBy([...data[uniqueID], newTable], 'freq')
        return data
    })
    // frequencyDatas.update((table) => uniqBy([...table, newTable], 'freq'))
    console.log('Line fitted', get(frequencyDatas))
}
