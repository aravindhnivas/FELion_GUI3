import { sumBy } from 'lodash-es'
import { boltzmanConstantInMHz, boltzmanConstantInWavenumber } from '$src/js/constants'
import { compute_Gj } from './balance_distribution'

export default function ({
    energyLevels = [], trapTemp = 5, electronSpin = false, zeemanSplit = false, energyUnit = 'cm-1',
}: BoltzmanDistributionOptions) {

    const kB = {
        MHz: boltzmanConstantInMHz,
        'cm-1': boltzmanConstantInWavenumber,
    }

    const KT = kB[energyUnit] * trapTemp
    
    try {
        const distribution = energyLevels.map(({ label, value: currentEnergy }) => {
            const Gj = compute_Gj({zeemanSplit, electronSpin, label})
            const value = Gj * Math.exp(-currentEnergy / KT)
            return { label, value }
        })

        // const partitionValue = Number(sumBy(distribution, (energy) => energy.value)).toFixed(2)
        const partitionValue = sumBy(distribution, (energy) => energy.value)
        const boltzmanDistribution = distribution.map(({ label, value }) => {
            const newvalue = value / partitionValue
            return { label, value: newvalue }
        })
        return { distribution: boltzmanDistribution, partitionValue }
    } catch (error) {
        window.handleError(error)
        return null
    }
}
