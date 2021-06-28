
export default function ({collisionalRateConstants, numberDensity, boltzmanDistribution}={}) {
    const energyKeys = boltzmanDistribution.map(f=>f.label)
    const ionCounts = {}
    boltzmanDistribution.forEach(f=>{ionCounts[f.label] = f.value})
    const rateConstants = {}
    collisionalRateConstants.forEach(f=>{rateConstants[f.label] = f.value})

    let collisionalCollection = []
    let collections = [];
    for (i of energyKeys) {
        for (j of energyKeys) {

            collections = [];

            const key = `${j} --> ${i}`
            const keyInverse = `${i} --> ${j}`
            if (i !== j) {

                
                numberDensity = parseFloat(numberDensity)
                const forward = rateConstants[key]*numberDensity*ionCounts[j];
                const reverse = rateConstants[keyInverse]*numberDensity*ionCounts[i]
                const currentValue =  forward - reverse
                collections = [...collections, currentValue]
            }
        }
        const currentCollection = {label:i, value:_.sum(collections), id:getID()}
        collisionalCollection = [...collisionalCollection, currentCollection]
    }

    return collisionalCollection
}