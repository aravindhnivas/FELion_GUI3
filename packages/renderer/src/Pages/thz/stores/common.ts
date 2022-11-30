import { derived, writable } from 'svelte/store'

export const electronSpin = writable<boolean>(false)
export const zeemanSplit = writable<boolean>(false)

export const configFile = writable(<string>window.db.get('ROSAA_configfile') ?? '')

export const currentLocation = derived(configFile, ($configFile) => {
    if (!window.fs.isFile($configFile)) return ''
    window.db.set('ROSAA_configfile', $configFile)
    return window.path.dirname($configFile)
})

export const output_dir = derived(currentLocation, ($currentLocation) => {
    if (!window.fs.isDirectory($currentLocation)) return ''
    const data_dir = window.path.join($currentLocation, 'output/data')
    window.fs.ensureDirSync(data_dir)
    return data_dir
})

export const figs_dir = derived(currentLocation, ($currentLocation) => {
    if (!window.fs.isDirectory($currentLocation)) return ''
    const figs_dir = window.path.join($currentLocation, 'output/figs')
    window.fs.ensureDirSync(figs_dir)
    return figs_dir
})

export const excitedTo = writable<string>('')
export const excitedFrom = writable<string>('')
export const trapTemp = writable<number>(5)

export const numberDensity = writable<string>('')
export const trapArea = writable<string>('')

export const collisionalTemp = writable<number>(7)
export const configLoaded = writable<boolean>(false)
export const plot_colors = writable('default')
