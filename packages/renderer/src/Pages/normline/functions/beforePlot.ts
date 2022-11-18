import { felixIndex, felixOutputName, normMethod, opoMode, felixData, opoData, get, delta } from './svelteWritables'
import { plot } from '../../../js/functions'

const get_data = (data: DataFromPython) => {
    let dataPlot = []
    for (const x in data) {
        dataPlot.push(data[x])
    }
    return dataPlot
}

const signal = {
    rel: 'Signal = (1-C/B)*100',
    log: 'Signal = -ln(C/B)/Power(in J)',
    hv: 'Signal = -ln(C/B)/#Photons',
}

export default async function beforePlot({
    dataFromPython,
    graphDiv,
    baseGraphDiv,
}: {
    dataFromPython: FELIXData
    graphDiv: string
    baseGraphDiv: string
}) {
    try {
        felixOutputName.set('averaged')
        felixIndex.set([])

        let avgdataToPlot: DataFromPython | undefined
        let signal_formula: string = ''
        let ylabel: string = ''

        if (get(normMethod) === 'Log') {
            avgdataToPlot = dataFromPython['average']
            signal_formula = 'Signal = -ln(C/B)/Power(in J)'
            ylabel = 'Normalised Intensity per J'
        } else if (get(normMethod) == 'Relative') {
            avgdataToPlot = dataFromPython['average_rel']
            signal_formula = 'Signal = (1-C/B)*100'
            ylabel = 'Relative Depletion (%)'
        } else if (get(normMethod) == 'IntensityPerPhoton') {
            avgdataToPlot = dataFromPython['average_per_photon']
            signal_formula = 'Signal = -ln(C/B)/#Photons'
            ylabel = 'Normalised Intensity per photon'
        }
        // console.warn(get(delta))
        const set_title = (method: 'rel' | 'log' | 'hv') =>
            `Normalised and Averaged Spectrum<br>${signal[method]}; {C=Measured Count, B=Baseline Count}`

        const normMethod_datas = {
            Relative: {
                data: get_data(dataFromPython['average_rel']),
                layout: {
                    title: set_title('rel'),
                    yaxis: { title: 'Relative Depletion (%)' },
                    xaxis: { title: 'Calibrated Wavelength (cm-1)' },
                },
            },
            Log: {
                data: get_data(dataFromPython['average']),
                layout: {
                    title: set_title('log'),
                    yaxis: { title: 'Normalised Intensity per J' },
                    xaxis: { title: 'Calibrated Wavelength (cm-1)' },
                },
            },
            IntensityPerPhoton: {
                data: get_data(dataFromPython['average_per_photon']),
                layout: {
                    title: set_title('hv'),
                    yaxis: { title: 'Normalised Intensity per photon' },
                    xaxis: { title: 'Calibrated Wavelength (cm-1)' },
                },
            },
        }

        if (get(opoMode)) {
            opoData.set(normMethod_datas)
        } else {
            felixData.set(normMethod_datas)
        }

        plot('Baseline Corrected', 'Wavelength (cm-1)', 'Counts', dataFromPython['base'], baseGraphDiv)

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
