import { plot } from '../../../js/functions'

export function theory_func({ dataFromPython, normMethod, uniqueID }) {
    let ylabel
    if (normMethod === 'Log') {
        ylabel = 'Normalised Intensity per J'
    } else if (normMethod === 'Relative') {
        ylabel = 'Relative Depletion (%)'
    } else {
        ylabel = 'Normalised Intensity per Photon'
    }

    let theoryData = []
    for (let x in dataFromPython['line_simulation']) {
        theoryData.push(dataFromPython['line_simulation'][x])
    }

    plot(
        'Experimental vs Theory',
        'Calibrated Wavelength (cm-1)',
        ylabel,
        [dataFromPython['averaged'], ...theoryData],
        `${uniqueID}-exp-theory-plot`
    )

    console.log('Graph Plotted')
}
