import { dataTable, opoMode, felixOutputName, fittedTraceCount, normMethods, fitted_data } from './svelteWritables'
import type { DataTable } from './svelteWritables'
import { addTraces } from 'plotly.js-basic-dist'
import { uniqBy } from 'lodash-es'

function getTable(data, name, color) {
    const table: DataTable[] = data.map((d) => {
        const { freq, amp, fwhm, sig } = d
        return {
            id: window.getID(),
            name,
            freq,
            amp,
            fwhm,
            sig,
            color,
        }
    })
    // table = uniqBy(table, 'freq')
    return table
}

export function NGauss_fit_func({ dataFromPython, uniqueID, normMethod }) {
    console.log({ dataFromPython })

    const currentGraph = opoMode.get(uniqueID) ? `${uniqueID}-opoRelPlot` : `${uniqueID}-avgplot`
    addTraces(currentGraph, dataFromPython[normMethod]['fitted_data'])
    fittedTraceCount.update((n) => {
        n[uniqueID] += 1
        return n
    })
    const output_name = felixOutputName.get(uniqueID)
    const color = output_name === 'averaged' ? '#836ac05c' : '#fafafa'

    fitted_data.setValue(uniqueID, {})

    normMethods.forEach((method) => {
        const methodData = dataFromPython[method]
        if (!methodData) return
        const data = methodData['fitted_parameter']
        const table = uniqBy(getTable(data, output_name, color), 'freq')
        if (method === normMethod) {
            dataTable.setValue(uniqueID, table)
        }
        fitted_data.update((data) => {
            data[uniqueID][method] = table
            return data
        })
    })
}
