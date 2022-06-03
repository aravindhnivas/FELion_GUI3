import { plotlyEventCreatedOPO, get } from './svelteWritables'
import { plot } from '../../../js/functions'
import { plotlySelection, plotlyClick } from './misc'
import beforePlot from './beforePlot'

export async function opofile_func({ dataFromPython, delta } = {}) {
    try {
        await beforePlot({
            delta,
            dataFromPython,
            graphDiv: 'opoRelPlot',
            baseGraphDiv: 'opoplot',
        })
        plot('OPO Calibration', 'Set Wavenumber (cm-1)', 'Measured Wavenumber (cm-1)', dataFromPython['SA'], 'opoSA')
        if (!get(plotlyEventCreatedOPO)) {
            const plot = { graphDiv: 'opoRelPlot', mode: 'opo' }
            plotlySelection(plot), plotlyClick(plot)
            plotlyEventCreatedOPO.set(true)
        }
    } catch (error) {
        console.error(error)
    }
}
