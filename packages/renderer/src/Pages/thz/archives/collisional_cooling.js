import { Solver } from 'odex'

function computeODECollision({
    collisionalRateConstants,
    numberDensity,
    energyKeys,
}) {
    return function (t, y) {
        numberDensity = parseFloat(numberDensity)

        const ionCounts = {}
        energyKeys.forEach((key, index) => {
            ionCounts[key] = y[index]
        })

        const rateConstants = {}
        collisionalRateConstants.forEach((f) => {
            rateConstants[f.label] = f.value
        })

        const collisionalCollection = []

        for (const i of energyKeys) {
            const collections = []

            for (const j of energyKeys) {
                const key = `${j} --> ${i}`
                const keyInverse = `${i} --> ${j}`

                if (i !== j) {
                    const forward =
                        rateConstants[key] * numberDensity * ionCounts[j]
                    const reverse =
                        rateConstants[keyInverse] * numberDensity * ionCounts[i]
                    const currentValue = forward - reverse
                    collections.push(currentValue)
                }
            }
            collisionalCollection.push(collections)
        }
        const dR_dT = collisionalCollection.map((collect) =>
            collect.reduce((a, b) => a + b)
        )
        return dR_dT
    }
}

onmessage = function ({
    data: {
        collisionalRateConstants,
        numberDensity,
        boltzmanDistribution,
        t0 = 0,
        duration,
        totalSteps,
    },
}) {
    console.log('Worker: Message received from main script')
    console.log('Starting ODE solver...')

    console.time('Collisional ODE solve')
    try {
        const initialValue = boltzmanDistribution.map((f) => f.value)
        console.log(initialValue, initialValue.length, 'solver length')

        const energyKeys = boltzmanDistribution.map((f) => f.label)

        duration *= 1e-3

        const solutionValues = []
        const simulationTime = []
        const tsteps = (duration - t0) / totalSteps
        console.log({ totalSteps, tsteps })
        const ODESolver = new Solver(initialValue.length)
        ODESolver.denseOutput = true
        ODESolver.solve(
            computeODECollision({
                collisionalRateConstants,
                numberDensity,
                energyKeys,
            }),
            t0,
            initialValue,
            duration,
            ODESolver.grid(tsteps, function (x, y) {
                simulationTime.push(x)
                solutionValues.push(y)
            })
        )
        console.log('ODE solved')
        const solutionByMolecule = solutionValues[0].map((_, colIndex) =>
            solutionValues.map((row) => row[colIndex])
        )
        const finalData = {}
        energyKeys.forEach((key, index) => {
            finalData[key] = {
                x: simulationTime,
                y: solutionByMolecule[index],
                name: key,
            }
        })

        console.timeEnd('Collisional ODE solve')
        postMessage({ finalData, error: null })
    } catch (error) {
        postMessage({ finalData: null, error })
    }
}
