import { writable, derived} from 'svelte/store';
import {get} from 'svelte/store';

export {get};

export const felixIndex = writable([])
export const felixPeakTable = writable([])
export const felixOutputName = writable("")
export const opoMode = writable(false)
export const Ngauss_sigma = writable(5)
export const dataTable = writable([])
export const dataTable_avg = writable([])

export const normMethodDatas = writable({})
export const felixopoLocation = writable("")
export const filedetails = writable([])

export const felixPlotAnnotations = writable([])

export const plotlyEventCreatedFELIX = writable(false)
export const plotlyEventCreatedOPO = writable(false)
export const graphDiv = derived(
    opoMode,
    $opoMode => {return $opoMode ? "opoRelPlot" : "avgplot" }
)

export const expfittedLines = writable([])
export const expfittedLinesCollectedData = writable([])
export const collectData = writable(false)
export const avgfittedLineCount = writable(0)
export const fittedTraceCount = writable(0)
export const felixAnnotationColor = writable("black")