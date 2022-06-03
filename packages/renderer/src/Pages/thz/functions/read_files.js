import { tick } from 'svelte'
import { browse } from '$components/Layout.svelte'

export async function readFromFile({
    bowseFile = true,
    energyFilename = null,
    electronSpin,
    zeemanSplit,
    energyUnit,
    twoLabel = true,
    collisionalFile = false,
} = {}) {
    if (!energyFilename || bowseFile) {
        const energyDetailsFile = await browse({ dir: false })

        if (energyDetailsFile) return Promise.reject('No files selected')
        energyFilename = energyDetailsFile[0]
    }

    const noSplittings = !electronSpin && !zeemanSplit
    const splittings = electronSpin || zeemanSplit
    const fileContents = window.fs.readFileSync(energyFilename).split('\n')
    let energyLevels = []

    let preLabel
    let value, label
    let numberOfLevels = 0
    let multilineComment = false
    let ground, excited
    let collisionalRateType
    fileContents.forEach((line) => {
        if (line.length > 1) {
            if (line.includes('//')) {
                if (line.includes('units')) {
                    energyUnit = line.split('=')[1].trim()
                } else if (line.includes('twoLabel')) {
                    twoLabel = Boolean(`${line.split('=')[1].trim()}`)
                } else if (collisionalFile && line.includes('mode')) {
                    collisionalRateType = line.split('=')[1].trim()
                    console.log(collisionalRateType)
                }
            } else if (line.includes('#') && splittings) {
                let currentLineLabel = line.split('#')[1]

                if (twoLabel) {
                    preLabel = currentLineLabel.split('\t').map((f) => f.trim())
                } else {
                    preLabel = currentLineLabel.trim()
                    numberOfLevels++
                }
            } else if (line.includes('{')) {
                multilineComment = true
            } else if (line.includes('}')) {
                multilineComment = false
            } else if (!multilineComment) {
                if (noSplittings) {
                    const lineSplitted = line.split('\t').map((f) => f.trim())
                    console.log(lineSplitted)
                    if (collisionalFile) {
                        label = `${lineSplitted[0]} --> ${lineSplitted[1]}`

                        value = lineSplitted[2]
                    } else {
                        label = twoLabel ? `${numberOfLevels + 1} --> ${numberOfLevels}` : numberOfLevels
                        value = lineSplitted[0]
                        numberOfLevels++
                    }
                } else {
                    line = line.split('\t').map((f) => f.trim())
                    const separator = electronSpin && zeemanSplit ? '__' : '_'

                    if (twoLabel) {
                        ;[ground, excited] = preLabel
                        label = `${excited}${separator}${line[1]} --> ${ground}${separator}${line[0]}`
                    } else {
                        value = line[1]
                        label = preLabel + separator + line[0]
                    }
                }

                energyLevels = [...energyLevels, { label, value, id: window.getID() }]
            }
        }
    })

    await tick()

    window.createToast('Energy file read: ' + window.path.basename(energyFilename))

    console.log(energyLevels)
    return Promise.resolve({
        energyLevels,
        numberOfLevels,
        energyFilename,
        energyUnit,
        collisionalRateType,
    })
}
