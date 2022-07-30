import DLSFit from 'ml-levenberg-marquardt'

onmessage = async function ({ data: { fileContents = '', collisionalTemp = 5 } }) {
    console.log('Running worker')
    const data = fileContents
        .split('\n')
        .filter((line) => !line.includes('#') && line.trim().length)
        .filter((line) => line.trim().split('\n'))

    console.log({ data })
    const temperature = data[0].split('\t').map((temp) => parseFloat(temp))
    console.log({ temperature })

    const rateConstantsRawData = data.slice(1)

    const rateConstants = []
    const originalDataToPlot = {}

    rateConstantsRawData.forEach((currentRate) => {
        currentRate = currentRate
            .trim()
            .split('\t')
            .map((r) => r.trim())
        console.log({ currentRate })

        const [i, j] = [currentRate[0], currentRate[1]]
        const label = `${i} --> ${j}`

        const currentRequiredRateData = currentRate.slice(2, 2 + temperature.length).map((r) => parseFloat(r))

        const dataToFit = {
            x: temperature,
            y: currentRequiredRateData,
        }
        console.log(dataToFit)

        originalDataToPlot[label] = {
            ...dataToFit,
            name: label,
        }

        const fittedParams = DLSFit(
            dataToFit,
            ([m, c]) =>
                (x) =>
                    m * x + c,
            { initialValues: [1e-6, 0] }
        )

        // console.log(fittedParams)
        const { parameterValues } = fittedParams
        const [m, c] = parameterValues

        // console.log({m, c})
        const fittedRateConstant = m * collisionalTemp + c
        const requiredRate = {
            label,
            value: fittedRateConstant.toExponential(3),
        }
        rateConstants.push(requiredRate)
    })
    postMessage({ rateConstants, originalDataToPlot })
}
