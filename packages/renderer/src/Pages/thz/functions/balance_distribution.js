import {
    boltzmanConstantInMHz,
    boltzmanConstantInWavenumber,
} from '$src/js/constants'

export default function ({
    label,
    energyLevels,
    collisionalTemp = 5,
    electronSpin = false,
    zeemanSplit = false,
    energyUnit = 'cm-1',
} = {}) {
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

        const energy_levels = {}
        energyLevels.forEach((f) => (energy_levels[f.label] = f.value))

        const delE = energy_levels[final] - energy_levels[initial]
        const rateConstant = Gw * Math.exp(delE / KT)
        return rateConstant.toExponential(3)
    } catch (error) {
        console.error(error)
        window.createToast('Error occured', 'danger')
        return null
    }
}

export function computeStatisticalWeight({
    electronSpin = false,
    zeemanSplit = false,
    final,
    initial,
} = {}) {
    let Gi, Gf

    if (!zeemanSplit) {
        if (electronSpin) {
            Gi = 2 * +initial.split('_')[1] + 1
            Gf = 2 * +final.split('_')[1] + 1
        } else {
            Gi = 2 * +initial + 1
            Gf = 2 * +final + 1
        }
    } else {
        ;(Gi = 1), (Gf = 1)
    }
    return { Gi, Gf }
}
