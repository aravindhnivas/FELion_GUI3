import {
    dataTable,
    graphDiv,
    felixOutputName,
    fittedTraceCount,
    normMethod,
    normMethods,
    get,
} from './svelteWritables'
import { addTraces } from 'plotly.js/dist/plotly-basic'
import { uniqBy } from 'lodash-es'
import { writable } from 'svelte/store'

function getTable(data, name, color) {
    const table = data.map((d) => {
        const { freq, amp, fwhm, sig } = d
        return {
            id: window.getID(),
            name, freq, amp, fwhm, sig, color,
        }
    })
    return uniqBy(table, 'freq')
}

export const fitted_data = writable({})

export function NGauss_fit_func({ dataFromPython }) {
    
    console.log({dataFromPython})

    addTraces(get(graphDiv), dataFromPython[get(normMethod)]['fitted_data'])
    fittedTraceCount.update((n) => n + 1)
    const output_name = get(felixOutputName)
    const color = output_name === 'averaged' ? '#836ac05c' : '#fafafa'
    
    fitted_data.set({})
    
    normMethods.forEach((method) => {
        const methodData = dataFromPython[method]
        if(!methodData) return
        const data = methodData['fitted_parameter']
        const table = getTable(data, output_name, color)
        if(method === get(normMethod)) {
            dataTable.set(table)
        }
        fitted_data.update((d) => ({
            ...d,
            [method]: table,
        }))
    })

    // // dataTable_avg
    // if (output_name === 'averaged') {
    //     let newTable = dataFromPython[get(normMethod)]['fitted_parameter'].map((data, index) => {
    //         let { freq, amp, fwhm, sig } = data

    //         return {
    //             name: `Line #${index}`,
    //             id: window.getID(),
    //             freq: freq,
    //             amp: amp,
    //             fwhm: fwhm,
    //             sig: sig,
    //             color: color,
    //         }
    //     })
    //     dataTable_avg.set(uniqBy(newTable, 'freq'))
    //     avgfittedLineCount.set(get(dataTable_avg).length)
    // }
}
