import {
    get,
    graphDiv,
    dataTable,
    collectData,
    dataTable_avg,
    expfittedLines,
    felixOutputName,
    fittedTraceCount,
    avgfittedLineCount,
    felixPlotAnnotations,
    expfittedLinesCollectedData,
} from './svelteWritables'
import { relayout, addTraces } from 'plotly.js/dist/plotly-basic'
import { uniqBy } from 'lodash-es'

export function exp_fit_func({ dataFromPython } = {}) {
    addTraces(get(graphDiv), dataFromPython['fit'])
    fittedTraceCount.update((n) => n + 1)

    expfittedLines.update((lines) => [...lines, ...dataFromPython['line']])
    relayout(get(graphDiv), { shapes: get(expfittedLines) })

    let annotations = dataFromPython['annotations']

    felixPlotAnnotations.update((annotate) => [...annotate, annotations])

    relayout(get(graphDiv), { annotations: get(felixPlotAnnotations) })

    let [freq, amp, fwhm, sig] = dataFromPython['table'].split(', ')

    let color = '#fafafa'

    const output_name = get(felixOutputName)
    if (output_name === 'averaged') {
        color = '#836ac05c'
        dataTable_avg.update((table) => [
            ...table,
            {
                name: `Line #${get(avgfittedLineCount)}`,
                id: getID(),
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
            expfittedLinesCollectedData.update((data) => [
                ...data,
                dataFromPython['for_weighted_error'],
            ])
        }
    }
    let newTable = {
        name: output_name,
        id: getID(),
        freq,
        amp,
        fwhm,
        sig,
        color,
    }
    dataTable.update((table) => uniqBy([...table, newTable], 'freq'))

    console.log('Line fitted')
}
