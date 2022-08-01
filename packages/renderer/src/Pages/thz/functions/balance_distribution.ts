import {energyLevels, get_KT} from '../stores/energy';
import {zeemanSplit, electronSpin } from '../stores/common';
import {get} from 'svelte/store';

export default function ({
    label = '',
    collisionalTemp = 5,
}: BalanceDistributionOptions) {
    
    const KT = get_KT(collisionalTemp)

    try {
        const [initial, final] = label.split(' --> ').map((f) => f.trim())
        const { Gi, Gf } = computeStatisticalWeight({
            final,
            initial,
        })
        const Gw = Gi / Gf

        const energy_levels: KeyStringObj<number> = {}
        get(energyLevels).forEach((f) => (energy_levels[f.label] = f.value))

        const delE = energy_levels[final] - energy_levels[initial]
        const rateConstant = Gw * Math.exp(delE / KT)
        return rateConstant
    } catch (error) {
        console.error(error)
        window.createToast('Error occured', 'danger')
        return null
    }
}

export function compute_Gj(label: string){
    if(get(zeemanSplit)){
        return 1
    } else if(get(electronSpin)){
        const j = parseFloat(label.split('_')[1])
        return 2 * j + 1
    } else {
        return 2 * +label + 1
    }
}

export function computeStatisticalWeight({ final, initial }: ComputeStatisticalWeightOptions) {
    const Gi = compute_Gj(initial)
    const Gf = compute_Gj(final)
    return { Gi, Gf }
}
