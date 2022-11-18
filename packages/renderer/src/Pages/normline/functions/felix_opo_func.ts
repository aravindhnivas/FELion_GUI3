import { subplot, plot } from '../../../js/functions'
import { plotlySelection, plotlyClick } from './misc'
import beforePlot from './beforePlot'

export async function felix_opo_func({
    dataFromPython,
    uniqueID,
    mode,
}: {
    dataFromPython: FELIXData
    uniqueID: string
    mode: 'felix' | 'opo'
}) {
    let baseGraphDiv: string
    let graphDiv: string

    if (mode === 'felix') {
        graphDiv = `${uniqueID}-avgplot`
        baseGraphDiv = `${uniqueID}-bplot`
    } else if (mode === 'opo') {
        graphDiv = `${uniqueID}-opoRelPlot`
        baseGraphDiv = `${uniqueID}-opoplot`
    }

    const status = await beforePlot({
        dataFromPython,
        graphDiv,
        baseGraphDiv,
    })

    if (!status) return console.warn('No data to plot')

    if (mode === 'felix') {
        if (dataFromPython['SA'] && dataFromPython['pow']) {
            subplot(
                'Spectrum and Power Analyser',
                'Wavelength set (cm-1)',
                'SA (cm-1)',
                dataFromPython['SA'],
                `${uniqueID}-saPlot`,
                'Wavelength (cm-1)',
                'Total Power (mJ)',
                dataFromPython['pow']
            )
        }

        console.log('Graph Plotted')
    } else if (mode === 'opo') {
        plot(
            'OPO Calibration',
            'Set Wavenumber (cm-1)',
            'Measured Wavenumber (cm-1)',
            dataFromPython['SA'],
            `${uniqueID}-opoSA`
        )
    }

    const currentGraphDiv = document.getElementById(graphDiv)

    const event = new CustomEvent('plotted', { bubbles: false, detail: { graphDiv } })
    currentGraphDiv.dispatchEvent(event)

    if (currentGraphDiv.hasAttribute('data-plotly-event-created')) return

    const plotDetails = { graphDiv, mode }
    currentGraphDiv.setAttribute('data-plotly-event-created', 'true')

    plotlySelection(plotDetails)
    plotlyClick(plotDetails)
}
