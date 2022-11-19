import {
    get,
    opoMode,
    dataTable,
    dataTable_avg,
    frequencyDatas,
    expfittedLines,
    felixOutputName,
    fittedTraceCount,
    felixPlotAnnotations,
} from './svelteWritables'

import { relayout, addTraces } from 'plotly.js-basic-dist'
import { uniqBy } from 'lodash-es'

export function exp_fit_func({ dataFromPython, uniqueID }: { dataFromPython: any; uniqueID: string }) {
    const currentGraph = opoMode.get(uniqueID) ? `${uniqueID}-opoRelPlot` : `${uniqueID}-avgplot`

    if (!dataFromPython?.['fit']) return window.createToast('No data available to fit', 'danger')
    addTraces(currentGraph, dataFromPython['fit'])
    fittedTraceCount.update((n) => {
        n[uniqueID] += 1
        return n
    })

    console.log(dataFromPython)
    expfittedLines.update((lines) => {
        lines[uniqueID] = [...lines[uniqueID], dataFromPython['line']]
        return lines
    })
    relayout(currentGraph, { shapes: expfittedLines.get(uniqueID) })

    const annotations = dataFromPython['annotations']

    felixPlotAnnotations.update((data) => {
        data[uniqueID] = uniqBy([...data[uniqueID], annotations], 'text')
        return data
    })
    relayout(currentGraph, { annotations: felixPlotAnnotations.get(uniqueID) })

    let [freq, amp, fwhm, sig] = dataFromPython['table'].split(', ')

    let color = '#fafafa'

    const output_name = felixOutputName.get(uniqueID) as string
    if (output_name === 'averaged') {
        color = '#836ac05c'
        const total_lines = dataTable_avg.get(uniqueID).length
        const newTable = {
            name: `Line #${total_lines}`,
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

    dataTable.update((data) => {
        data[uniqueID] = uniqBy([...data[uniqueID], newTable], 'freq')
        return data
    })
    frequencyDatas.update((data) => {
        data[uniqueID] = uniqBy([...data[uniqueID], newTable], 'freq')
        return data
    })
    console.log('Line fitted', get(frequencyDatas))
}
