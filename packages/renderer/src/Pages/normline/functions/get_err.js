import { dataTable, dataTable_avg } from './svelteWritables'

export function get_err_func({ dataFromPython } = {}) {
    let { freq, amp, fwhm, sig } = dataFromPython
    let data1 = {
        name: 'unweighted_mean',
        id: getID(),
        freq: freq.mean,
        amp: amp.mean,
        fwhm: fwhm.mean,
        sig: sig.mean,
        color: '#f14668',
    }

    let data2 = {
        name: 'weighted_mean',
        id: getID(),
        freq: freq.wmean,
        amp: amp.wmean,
        fwhm: fwhm.wmean,
        sig: sig.wmean,
        color: '#2098d1',
    }

    dataTable.update((table) => [...table, data1, data2])
    dataTable_avg.update((table) => [...table, data1, data2])

    console.log('Weighted fit.')
}
