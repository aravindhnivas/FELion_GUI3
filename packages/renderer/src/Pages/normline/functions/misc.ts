import {
    felixopoLocation,
    felixPeakTable,
    felixIndex,
    felixOutputName,
    felixPlotAnnotations,
    opoMode,
    Ngauss_sigma,
    get,
} from './svelteWritables'
import { relayout } from 'plotly.js-basic-dist'
import { uniqBy } from 'lodash-es'

export function savefile({ file = {}, name = '', location = '' } = {}) {
    const filestem = name.endsWith('.json') ? name : `${name}.json`
    const filename = window.path.join(location, filestem)
    const result = window.fs.outputJsonSync(filename, { file })
    if (window.fs.isError(result)) {
        return window.handleError(result)
    }
    window.createToast(`${name}.json has been saved.`, 'success')
}

export function loadfile(name, location) {
    const filestem = name.endsWith('.json') ? name : `${name}.json`
    const filename = window.path.join(location, filestem)
    if (!window.fs.isFile(filename)) {
        window.createToast(`Invalid file: ${name}.json .`, 'danger')
        return []
    }

    const getdata = window.fs.readJsonSync(filename)
    if (window.fs.isError(getdata)) {
        window.handleError(getdata)
        return []
    }

    const loadedfile = getdata?.file?.map((arr) => ({ ...arr, id: window.getID() })) || []
    window.createToast(`${name}.json has been loaded.`, 'success')

    return loadedfile
}

export function plotlySelection({ graphDiv, mode, uniqueID }) {
    const graph = document.getElementById(graphDiv)
    console.warn('Creating plotly selection events for, ', graphDiv)

    graph.on('plotly_selected', (data) => {
        try {
            console.log(data)
            mode === 'felix' ? opoMode.set(false) : opoMode.set(true)

            const { range } = data
            felixIndex.setValue(uniqueID, range.x)
            console.warn('felixIndex', get(felixIndex))

            let outputName = data.points[0]?.data?.name
            outputName = outputName.split('(')[0].split('.')[0]
            felixOutputName.setValue(uniqueID, outputName)
            // console.log('felixOutputName', felixOutputName.get(uniqueID))
        } catch (error) {
            console.log('No data available to fit')
        }
    })
}
export function plotlyClick({ graphDiv, mode, uniqueID }: { graphDiv: string; mode: string; uniqueID: string }) {
    const graph = document.getElementById(graphDiv)
    console.warn('Creating plotly click events for, ', graphDiv)

    graph.on('plotly_click', (data) => {
        console.log('Graph clicked: ', data)

        if (data.event.ctrlKey) {
            console.log('Data point length: ', data.points.length)

            for (let i = 0; i < data.points.length; i++) {
                console.log('Running cycle: ', i)

                let d = data.points[i]
                let name = d.data.name
                mode === 'felix' ? opoMode.set(false) : opoMode.set(true)

                const outputName = felixOutputName.get(uniqueID)
                // let outputName = data.points[0]?.data?.name
                // outputName = outputName.split('(')[0].split('.')[0]
                // felixOutputName.setValue(uniqueID, outputName)

                console.log('felixOutputName', outputName)
                console.log(name, outputName)
                if (!name.includes(outputName)) {
                    return window.createToast('Change output filename.', 'danger')
                }

                const { color } = d.data?.line
                const [freq, amp] = [parseFloat(d.x.toFixed(2)), parseFloat(d.y.toFixed(2))]
                const annotation = {
                    text: `(${freq}, ${amp})`,
                    x: freq,
                    y: amp,
                    font: { color },
                    arrowcolor: color,
                }

                felixPlotAnnotations.update((data) => {
                    data[uniqueID] = uniqBy([...data[uniqueID], annotation], 'text')
                    return data
                })
                console.log(felixPlotAnnotations.get(), felixPlotAnnotations.get(uniqueID))
                relayout(graphDiv, {
                    annotations: felixPlotAnnotations.get(uniqueID),
                })

                const currentPeaks = { freq, amp, sig: get(Ngauss_sigma), id: window.getID() }
                felixPeakTable.update((data) => {
                    data[uniqueID] = uniqBy([...data[uniqueID], currentPeaks], 'freq')
                    return data
                })
            }
        }
    })
}
