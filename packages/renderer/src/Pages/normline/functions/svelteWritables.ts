import { writable, derived } from 'svelte/store'
import { get } from 'svelte/store'
import { getfiles, customStore } from './stores/func'
export { get }

export const felixIndex = customStore([])
export const felixPeakTable = customStore<{ freq: number; amp: number; sig: number; id: string }[]>([])
export const felixOutputName = customStore('averaged')
export const opoMode = customStore(false)
export const Ngauss_sigma = customStore(5)

export interface DataTable {
    id: string
    name: string
    freq: number
    amp: number
    fwhm: number
    sig: number
    color: string
}

export const dataTable = customStore<DataTable[]>([])
export const dataTable_avg = customStore<DataTable[]>([])
export const frequencyDatas = customStore<DataTable[]>([])
export const fitted_data = customStore<{ [name: string]: DataTable[] }>({})

export const felixopoLocation = customStore('')
export const felixPlotAnnotations = customStore<Partial<Plotly.Annotations>[]>([])
export const expfittedLines = customStore<Plotly.Shape[]>([])
export const fittedTraceCount = customStore(0)
export const normMethods = ['Log', 'Relative', 'IntensityPerPhoton']
