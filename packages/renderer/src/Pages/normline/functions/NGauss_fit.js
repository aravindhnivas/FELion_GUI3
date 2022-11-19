import { dataTable, opoMode, felixOutputName, fittedTraceCount, normMethod, normMethods, get } from './svelteWritables'
import { addTraces } from 'plotly.js-basic-dist'
import { uniqBy } from 'lodash-es'
import { writable } from 'svelte/store'

function getTable(data, name, color) {
    const table = data.map((d) => {
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
    return uniqBy(table, 'freq')
}

export const fitted_data = writable({})

export function NGauss_fit_func({ dataFromPython, uniqueID }) {
    console.log({ dataFromPython })

    const currentGraph = get(opoMode) ? `${uniqueID}-opoRelPlot` : `${uniqueID}-avgplot`
    addTraces(currentGraph, dataFromPython[get(normMethod)]['fitted_data'])
    fittedTraceCount.update((n) => n + 1)
    const output_name = felixOutputName.get(uniqueID)
    const color = output_name === 'averaged' ? '#836ac05c' : '#fafafa'

    fitted_data.set({})

    normMethods.forEach((method) => {
        const methodData = dataFromPython[method]
        if (!methodData) return
        const data = methodData['fitted_parameter']
        const table = getTable(data, output_name, color)
        if (method === get(normMethod)) {
            dataTable.set(table)
        }
        fitted_data.update((d) => ({
            ...d,
            [method]: table,
        }))
    })
}
