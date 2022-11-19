import { felixIndex, felixOutputName } from './svelteWritables'
import { plot } from '../../../js/functions'

const get_data = (data: DataFromPython) => {
    let dataPlot = []
    for (const x in data) {
        dataPlot.push(data[x])
    }
    return dataPlot
}

export default async function beforePlot({
    dataFromPython,
    graphDiv,
    baseGraphDiv,
    uniqueID,
    normMethod,
}: {
    dataFromPython: FELIXData
    graphDiv: string
    baseGraphDiv: string
    uniqueID: string
    normMethod: string
}) {
    try {
        felixOutputName.setValue(uniqueID, 'averaged')
        felixIndex.setValue(uniqueID, [])

        let avgdataToPlot: DataFromPython
        let signal_formula: string = ''
        let ylabel: string = ''

        if (normMethod === 'Log') {
            avgdataToPlot = dataFromPython['average']
            ylabel = 'Normalised Intensity per J'
        } else if (normMethod == 'Relative') {
            avgdataToPlot = dataFromPython['average_rel']
            ylabel = 'Relative Depletion (%)'
        } else if (normMethod == 'IntensityPerPhoton') {
            avgdataToPlot = dataFromPython['average_per_photon']
            ylabel = 'Normalised Intensity per photon'
        }

        plot('Baseline Corrected', 'Wavelength (cm-1)', 'Counts', dataFromPython['base'], baseGraphDiv)

        // console.warn(normMethod, avgdataToPlot)
        if (!avgdataToPlot) return window.createToast('No data to plot', 'danger')

        plot(
            `Normalised and Averaged Spectrum<br>${signal_formula}; {C=Measured Count, B=Baseline Count}`,
            'Calibrated Wavelength (cm-1)',
            ylabel,
            avgdataToPlot,
            graphDiv
        )
        return Promise.resolve(true)
    } catch (error) {
        window.handleError(error)
    }
}
