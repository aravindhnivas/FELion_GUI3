// import { getContext } from 'svelte'
import { normMethod, normMethodDatas, opoMode, get } from './svelteWritables'
import { subplot, plot } from '$src/js/functions'
import { react } from 'plotly.js-basic-dist'
import { felix_func } from './felix'
import { opofile_func } from './opofile'
// const uniqueID = getContext('uniqueID')
export const get_data = (data) => {
    let dataPlot = []
    for (const x in data) {
        dataPlot.push(data[x])
    }
    return dataPlot
}

export const mapNormMethodKeys = {
    Relative: 'average_rel',
    Log: 'average',
    IntensityPerPhoton: 'average_per_photon',
}

export default function ({ fullData, plotfile, graphPlotted, uniqueID }) {
    const data = fullData.data || null
    if (!data) return window.createToast('No data for ' + plotfile, 'danger')
    if (!data.average?.[plotfile]) return console.warn(plotfile, 'data is not available', data)

    const SA = {}
    const base = {}
    const pow = {}

    if (plotfile !== 'average') {
        base[plotfile + '_base'] = data['base'][plotfile + '_base']
        base[plotfile + '_line'] = data['base'][plotfile + '_line']

        const baseGraphDiv = get(opoMode) ? `${uniqueID}-opoplot` : `${uniqueID}-bplot`
        plot('Baseline Corrected', 'Wavelength (cm-1)', 'Counts', base, baseGraphDiv)

        if (get(opoMode)) {
            console.log('Updating OPO plots')
            if (data['SA']?.['Calibration']) {
                SA['Calibration'] = data['SA']['Calibration']
                SA['Calibration_fit'] = data['SA']['Calibration_fit']

                plot('OPO Calibration', 'Set Wavenumber (cm-1)', 'Measured Wavenumber (cm-1)', SA, `${uniqueID}-opoSA`)
            }
        } else {
            console.log('Updating FELIX plots')
            SA[plotfile] = data['SA'][plotfile]
            SA[plotfile + '_fit'] = data['SA'][plotfile + '_fit']

            pow[plotfile] = data['pow'][`${plotfile.split('.')[0]}.pow`]
            subplot(
                'Spectrum and Power Analyser',
                'Wavelength set (cm-1)',
                'SA (cm-1)',
                SA,
                `${uniqueID}-saPlot`,
                'Wavelength (cm-1)',
                `Total Power (mJ)`,
                pow
            )
        }
    }

    const dataToPlot = {}
    for (const key of ['average', 'average_rel', 'average_per_photon']) {
        const addData = {}
        addData[plotfile] = { ...data[key][plotfile], showlegend: true }
        dataToPlot[key] = addData
    }

    if (graphPlotted) {
        const currentKey = mapNormMethodKeys[get(normMethod)]
        const currentData = get_data(dataToPlot[currentKey])

        const { layout } = get(normMethodDatas)[get(normMethod)]

        const currentGraph = get(opoMode) ? `${uniqueID}-opoRelPlot` : `${uniqueID}-avgplot`
        react(currentGraph, currentData, layout)
    } else {
        const fn = get(opoMode) ? opofile_func : felix_func
        fn({ dataFromPython: dataToPlot, uniqueID })
        graphPlotted = true
    }
}
