import {
    dataTable,
    opoMode,
    felixOutputName,
    fittedTraceCount,
    normMethod,
    normMethods,
    fitted_data,
    get,
} from './svelteWritables'
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

export function NGauss_fit_func({ dataFromPython, uniqueID }) {
    console.log({ dataFromPython })

    const currentGraph = get(opoMode) ? `${uniqueID}-opoRelPlot` : `${uniqueID}-avgplot`
    addTraces(currentGraph, dataFromPython[get(normMethod)]['fitted_data'])
    fittedTraceCount.update((n) => n + 1)
    const output_name = felixOutputName.get(uniqueID)
    const color = output_name === 'averaged' ? '#836ac05c' : '#fafafa'

    fitted_data.setValue(uniqueID, {})

    normMethods.forEach((method) => {
        const methodData = dataFromPython[method]
        if (!methodData) return
        const data = methodData['fitted_parameter']
        const table = uniqBy(getTable(data, output_name, color), 'freq')
        if (method === get(normMethod)) {
            // dataTable.set(table)
            dataTable.setValue(uniqueID, table)
        }
        // fitted_data.update((d) => ({
        //     ...d,
        //     [method]: table,
        // }))
        fitted_data.update((data) => {
            // data[uniqueID] = { ...data[uniqueID], [method]: table }
            data[uniqueID][method] = table
            return data
        })
    })
}
