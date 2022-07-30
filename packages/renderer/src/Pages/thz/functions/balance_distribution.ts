import { boltzmanConstantInMHz, boltzmanConstantInWavenumber } from '$src/js/constants'

export default function ({
    label = '',
    energyLevels = [],
    collisionalTemp = 5,
    electronSpin = false,
    zeemanSplit = false,
    energyUnit = 'cm-1',
}: BalanceDistributionOptions) {
    const kB = {
        MHz: boltzmanConstantInMHz,
        'cm-1': boltzmanConstantInWavenumber,
    }

    const KT = kB[energyUnit] * collisionalTemp

    try {
        const [initial, final] = label.split(' --> ').map((f) => f.trim())
        const { Gi, Gf } = computeStatisticalWeight({
            electronSpin,
            zeemanSplit,
            final,
            initial,
        })
        const Gw = Gi / Gf

        const energy_levels: KeyStringObj<number> = {}
        energyLevels.forEach((f) => (energy_levels[f.label] = f.value))

        const delE = energy_levels[final] - energy_levels[initial]
        const rateConstant = Gw * Math.exp(delE / KT)
        return rateConstant
    } catch (error) {
        console.error(error)
        window.createToast('Error occured', 'danger')
        return null
    }
}

export function compute_Gj({zeemanSplit, electronSpin, label}: {
    zeemanSplit: boolean,
    electronSpin: boolean,
    label: string,
}){
    if(zeemanSplit){
        return 1
    } else if(electronSpin){
        const j = parseFloat(label.split('_')[1])
        return 2 * j + 1
    } else {
        return 2 * +label + 1
    }
}

export function computeStatisticalWeight({ electronSpin = false, zeemanSplit = false, final, initial }: ComputeStatisticalWeightOptions) {
    const Gi = compute_Gj({zeemanSplit, electronSpin, label: initial})
    const Gf = compute_Gj({zeemanSplit, electronSpin, label: final})
    return { Gi, Gf }
}
