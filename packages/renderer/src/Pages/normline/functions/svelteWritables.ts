import { writable, derived } from 'svelte/store'
import { get } from 'svelte/store'
import { getfiles, customStore } from './stores/func'
export { get }

export const felixIndex = customStore([])
export const felixPeakTable = customStore<{ freq: number; amp: number; sig: number; id: string }[]>([])
export const felixOutputName = customStore('averaged')
export const opoMode = writable(false)
export const Ngauss_sigma = writable(5)

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
export const opoData = writable({})
export const felixData = writable({})

export const normMethodDatas = derived([opoMode, felixData, opoData], ([$opoMode, $felixData, $opoData]) => {
    return $opoMode ? $opoData : $felixData
})

export const felixopoLocation = writable('')

export const theoryLocation = window.persistentDB('theoryLocation', '')

export const theoryfiles = derived([theoryLocation], ([$theoryLocation]) => getfiles($theoryLocation, '.txt'))

export const felixOpoDatLocation = derived([felixopoLocation], ([$felixopoLocation]) => {
    const data_location = window.path.resolve($felixopoLocation, '../EXPORT')
    if (!window.fs.isDirectory(data_location)) return ''
    return data_location
})

export const felixOpoDatfiles = derived([felixOpoDatLocation], ([$felixOpoDatLocation]) => {
    return getfiles($felixOpoDatLocation, '.dat')
})

export const felixPlotAnnotations = customStore<
    {
        x: number
        y: number
        text: string
        font?: { color: string }
        arrowcolor?: string
    }[]
>([])

export const expfittedLines = writable([])
export const expfittedLinesCollectedData = writable([])
export const collectData = writable(false)
export const avgfittedLineCount = writable(0)
export const fittedTraceCount = writable(0)

export const felixAnnotationColor = writable('black')
export const normMethods = ['Log', 'Relative', 'IntensityPerPhoton']
export const normMethod = writable('Relative')

export const felixPlotCheckboxes = writable([
    {
        label: 'DAT_file',
        options: [],
        value: [],
        id: window.getID(),
    },
    {
        label: 'Fundamentals',
        options: [],
        value: [],
        id: window.getID(),
    },
    {
        label: 'Others',
        options: [],
        value: [],
        id: window.getID(),
    },
    {
        label: 'Overtones',
        options: [],
        value: [],
        id: window.getID(),
    },
    {
        label: 'Combinations',
        options: [],
        value: [],
        id: window.getID(),
    },
])
