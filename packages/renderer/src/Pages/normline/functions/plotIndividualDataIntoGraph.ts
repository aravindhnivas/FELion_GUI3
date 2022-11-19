import { opoMode } from './svelteWritables'
import { plotlayout } from './plot_labels'
import { subplot, plot } from '$src/js/functions'
import { react } from 'plotly.js-basic-dist'
import { felix_opo_func } from './felix_opo_func'

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

export default function ({ fullData, plotfile, uniqueID, normMethod }) {
    const data = fullData.data || null
    if (!data) return window.createToast('No data for ' + plotfile, 'danger')
    if (!data.average?.[plotfile]) return console.warn(plotfile, 'data is not available', data)

    const SA = {}
    const base = {}
    const pow = {}

    if (plotfile !== 'average') {
        base[plotfile + '_base'] = data['base'][plotfile + '_base']
        base[plotfile + '_line'] = data['base'][plotfile + '_line']

        const baseGraphDiv = opoMode.get(uniqueID) ? `${uniqueID}-opoplot` : `${uniqueID}-bplot`
        plot('Baseline Corrected', 'Wavelength (cm-1)', 'Counts', base, baseGraphDiv)

        if (opoMode.get(uniqueID)) {
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

    const currentGraphID = opoMode.get(uniqueID) ? `${uniqueID}-opoRelPlot` : `${uniqueID}-avgplot`
    const currentGraph = document.getElementById(currentGraphID)
    if (currentGraph.hasAttribute('data-plotted')) {
        const currentKey = mapNormMethodKeys[normMethod]
        const currentData = get_data(dataToPlot[currentKey])
        react(currentGraph, currentData, plotlayout[normMethod])
    } else {
        const mode = opoMode.get(uniqueID) ? 'opo' : 'felix'
        felix_opo_func({ dataFromPython: dataToPlot, uniqueID, mode, normMethod })
    }
}
