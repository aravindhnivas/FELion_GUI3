import {energyLevels, get_KT} from '../stores/energy';
import {get} from 'svelte/store';
import { sumBy } from 'lodash-es'
import { compute_Gj } from './balance_distribution'

export default function (temperature: number) {

    const KT = get_KT(temperature)
    
    try {
        const distribution = get(energyLevels).map(({ label, value: currentEnergy }) => {
            const Gj = compute_Gj(label)
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
