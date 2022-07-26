import get_files_settings_values from '$src/js/get_files_settings_values'
// import Plotly from "plotly.js"
// export interface MassData {
//     [name: string] : {
//         x: number[]
//         y: number[]
//         showlegend: boolean
//         name: string
//         mode: "lines" | "markers" | "lines+markers"
//     }
// }
export async function readMassFile(massfiles: string[]) {
    
    const loadbtn = document.getElementById('masspec-plot-btn') as HTMLButtonElement
    if (loadbtn.classList.contains('is-loading')) {
        const warnmsg = new Error('Mass spec plot is already loading')
        // window.createToast(warnmsg.message, 'warning')
        return Promise.resolve([null, warnmsg])
    }
    
    loadbtn.classList.toggle('is-loading')
    
    try {

        const dataToSend: DataFromPython = {}

        for (const filename of massfiles) {
            if (!window.fs.isFile(filename)) return Promise.resolve([null, new Error(`File ${filename} does not exist`)])
            
            const [fileContents] = await window.fs.readFile(filename)
            if(!fileContents) return Promise.resolve([null, new Error(`File ${filename} is empty`)])

            const name = window.path.basename(filename)
            console.info('content read: ', name)
            const dataContents = fileContents
                .split('\n')
                .filter((line) => !line.includes('#'))
                .map((line) =>
                    line
                        .trim()
                        .split('\t')
                        .map((data) => parseFloat(data))
                )

            console.info(name, 'filtered')
            const [x, y] = dataContents[0].map((_, colIndex) => dataContents.map((row) => row[colIndex]))
            const mode = 'lines'
            const showlegend = true
            console.info(name, 'done\n')

            const fileVariableComputedValues = await get_files_settings_values(filename)
            const res = fileVariableComputedValues['m03_ao13_reso']
            const b0 = fileVariableComputedValues['m03_ao09_width'] / 1000
            const trap = fileVariableComputedValues['m04_ao04_sa_delay'] / 1000

            const label = `${name}: Res:${res?.toFixed(1)} V; B0: ${b0?.toFixed(0)} ms; trap: ${trap?.toFixed(0)} ms`
            dataToSend[name] = { x, y, name: label, mode, showlegend }

            console.warn(dataToSend)
        }

        console.info('File read completed')
        console.info(dataToSend)
        return Promise.resolve([dataToSend, null])

    } catch (error) {

        if(error instanceof Error) {
        
            window.handleError(error)
            return Promise.resolve([null, error])
        }
    } finally {
        loadbtn.classList.toggle('is-loading')
    }
}
