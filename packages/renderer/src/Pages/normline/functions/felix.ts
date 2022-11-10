import { plotlyEventCreatedFELIX, felixGraphPlotted, get } from './svelteWritables'
import { subplot } from '../../../js/functions'
import { plotlySelection, plotlyClick } from './misc'
import beforePlot from './beforePlot'
// import { relayout } from 'plotly.js-basic-dist'

export async function felix_func({ dataFromPython }: { dataFromPython: FELIXData }) {
    const status = await beforePlot({
        dataFromPython,
        graphDiv: 'avgplot',
        baseGraphDiv: 'bplot',
    })

    if (!status) return console.warn('No data to plot')
    if (dataFromPython['SA'] && dataFromPython['pow']) {
        subplot(
            'Spectrum and Power Analyser',
            'Wavelength set (cm-1)',
            'SA (cm-1)',
            dataFromPython['SA'],
            'saPlot',
            'Wavelength (cm-1)',
            'Total Power (mJ)',
            dataFromPython['pow']
        )
    }
    if (!get(plotlyEventCreatedFELIX)) {
        const plot = { graphDiv: 'avgplot', mode: 'felix' }
        plotlySelection(plot), plotlyClick(plot)
        plotlyEventCreatedFELIX.set(true)
    }
    console.log('Graph Plotted')
    felixGraphPlotted.set(true)
}
