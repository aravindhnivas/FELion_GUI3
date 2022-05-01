import { filedetails } from './svelteWritables'

export function get_details_func({ dataFromPython } = {}) {
    const info = dataFromPython.files.map((data) => {
        const { filename, trap, res, b0, range } = data
        const [min, max] = range
        return {
            filename,
            min,
            max,
            trap,
            b0,
            res,
            precursor: '',
            ie: '',
            temp: '',
            id: getID(),
        }
    })
    filedetails.set(info)
}
