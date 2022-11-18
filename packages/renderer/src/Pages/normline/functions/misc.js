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
    const filename = window.path.join(location || get(felixopoLocation), filestem)
    const result = window.fs.outputJsonSync(filename, { file })
    if (window.fs.isError(result)) {
        return window.handleError(result)
    }
    window.createToast(`${name}.json has been saved.`, 'success')
}

export function loadfile(name) {
    const filestem = name.endsWith('.json') ? name : `${name}.json`
    const filename = window.path.join(get(felixopoLocation), filestem)
    // const filename = window.path.join(get(felixopoLocation), `${name}.json`)
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

export function plotlySelection({ graphDiv, mode }) {
    const graph = document.getElementById(graphDiv)
    console.warn('Creating plotly selection events for, ', graphDiv)

    graph.on('plotly_selected', (data) => {
        try {
            console.log(data)
            mode === 'felix' ? opoMode.set(false) : opoMode.set(true)

            const { range } = data
            felixIndex.set(range.x)

            let outputName = data.points[0]?.data?.name
            outputName = outputName.split('(')[0].split('.')[0]
            console.log({ outputName })
            felixOutputName.set(outputName)
        } catch (error) {
            console.log('No data available to fit')
        }
    })
}

export function plotlyClick({ graphDiv, mode }) {
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

                const outputName = get(felixOutputName)

                if (name.includes(outputName)) {
                    const { color } = d.data?.line
                    const [freq, amp] = [parseFloat(d.x.toFixed(2)), parseFloat(d.y.toFixed(2))]
                    const annotation = {
                        text: `(${freq}, ${amp})`,
                        x: freq,
                        y: amp,
                        font: { color },
                        arrowcolor: color,
                    }

                    felixPlotAnnotations.update((annotate) => uniqBy([...annotate, annotation], 'text'))
                    relayout(graphDiv, {
                        annotations: get(felixPlotAnnotations),
                    })

                    felixPeakTable.update((table) => [
                        ...table,
                        { freq, amp, sig: get(Ngauss_sigma), id: window.getID() },
                    ])
                    felixPeakTable.update((table) => uniqBy(table, 'freq'))
                }
            }
        }
    })
}
