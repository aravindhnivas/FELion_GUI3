import {SpeedOfLight} from '$src/js/constants'
import { parse as Yml } from 'yaml'

export const wavenumberToMHz = (energy: ValueLabel<number>) => ({
    ...energy,
    value: Number(energy.value * SpeedOfLight * 1e2 * 1e-6)
})

export const MHzToWavenumber = (energy: ValueLabel<number>) => ({
    ...energy,
    value: Number(energy.value / (SpeedOfLight * 1e2 * 1e-6))
})

export const getYMLFileContents = async (filename: string) => {
    if (!window.fs.isFile(filename)) return Promise.reject(filename + " file doesn't exist")
    const fileContent = window.fs.readFileSync(filename)
    if (window.fs.isError(fileContent)) return Promise.reject("Couldn't read file " + filename)
    const YMLcontent = Yml(fileContent)
    return Promise.resolve(YMLcontent)
}

export const setID = <T extends OnlyValueLabel<T['value']>>(obj: T): ValueLabel<T['value']> => ({
    ...obj,
    id: window.getID(),
})

export const correctObjValue = (obj: ValueLabel) => ({
    ...obj,
    value: Number(obj.value).toExponential(3),
})
