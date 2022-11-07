import { writable, derived } from 'svelte/store'
import { get } from 'svelte/store'

export { get }

export const felixIndex = writable([])
export const felixPeakTable = writable([])

export const felixOutputName = writable('')
export const opoMode = writable(false)
export const Ngauss_sigma = writable(5)
export const dataTable = writable([])

export const dataTable_avg = writable([])

export const opoData = writable({})

export const felixData = writable({})

export const normMethodDatas = derived([opoMode, felixData, opoData], ([$opoMode, $felixData, $opoData]) => {
    return $opoMode ? $opoData : $felixData
})
export const felixopoLocation = writable('')
export const felixOpoDatLocation = derived([felixopoLocation], ([$felixopoLocation]) => {
    const data_location = window.path.resolve($felixopoLocation, '../EXPORT')
    if (!window.fs.isDirectory(data_location)) return ''
    return data_location
})
export const felixOpoDatfiles = derived([felixOpoDatLocation], ([$felixOpoDatLocation]) => {
    if (!$felixOpoDatLocation) return []
    const datfiles = window.fs
        .readdirSync($felixOpoDatLocation)
        .filter((f) => f.endsWith('.dat'))
        .map((f) => ({ name: f, id: window.getID() }))
    return datfiles
})
export const baselineFile = writable('')

export const filedetails = writable([])
export const felixPlotAnnotations = writable([])
export const plotlyEventCreatedFELIX = writable(false)
export const plotlyEventCreatedOPO = writable(false)
export const theoryRow = writable(false)
export const graphDiv = derived(opoMode, ($opoMode) => {
    return $opoMode ? 'opoRelPlot' : 'avgplot'
})

export const baseGraphDiv = derived(opoMode, ($opoMode) => {
    return $opoMode ? 'opoplot' : 'bplot'
})
export const expfittedLines = writable([])
export const expfittedLinesCollectedData = writable([])
export const collectData = writable(false)
export const avgfittedLineCount = writable(0)
export const fittedTraceCount = writable(0)

export const felixAnnotationColor = writable('black')

export const normMethods = ['Log', 'Relative', 'IntensityPerPhoton']
export const normMethod = writable('Relative')

export const frequencyDatas = writable([])

export const felixPlotCheckboxes = writable([])
export const showall = writable(true)
export const showRawData = writable(true)

export const showPowerData = writable(true)
export const felixGraphPlotted = writable(false)
export const OPOGraphPlotted = writable(false)
export const deltaOPO = writable(0.3)
export const deltaFELIX = writable(1)
export const delta = derived([opoMode, deltaOPO, deltaFELIX], ([$opoMode, $deltaOPO, $deltaFELIX]) => {
    return $opoMode ? $deltaOPO : $deltaFELIX
})
