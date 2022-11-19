import {
    get,
    opoMode,
    dataTable,
    collectData,
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

    let annotations = dataFromPython['annotations']

    // felixPlotAnnotations.update((annotate) => [...annotate, annotations])
    felixPlotAnnotations.update(uniqueID, annotations, 'text')
    // relayout(currentGraph, { annotations: get(felixPlotAnnotations) })
    relayout(currentGraph, { annotations: get(felixPlotAnnotations)[uniqueID] })

    let [freq, amp, fwhm, sig] = dataFromPython['table'].split(', ')

    let color = '#fafafa'

    const output_name = felixOutputName.get(uniqueID)
    if (output_name === 'averaged') {
        color = '#836ac05c'
        dataTable_avg.update((table) => [
            ...table,
            {
                name: `Line #${get(avgfittedLineCount)}`,
                id: window.getID(),
                freq,
                amp,
                fwhm,
                sig,
                color,
            },
        ])
        dataTable_avg.update((table) => uniqBy(table, 'freq'))
        avgfittedLineCount.update((n) => n + 1)
    } else {
        if (get(collectData)) {
            console.log('Collecting lines')
            expfittedLinesCollectedData.update((data) => [...data, dataFromPython['for_weighted_error']])
        }
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

    dataTable.update((table) => uniqBy([...table, newTable], 'freq'))
    frequencyDatas.update((table) => uniqBy([...table, newTable], 'freq'))
    console.log('Line fitted', get(frequencyDatas))
}
