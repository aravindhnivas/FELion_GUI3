export as namespace ROSAA;
interface AttachmentRate {
    constant: ValueLabel[]
    rate: ValueLabel[]
}

type EnergyLevels = ValueLabel<number>[]
type EnergyUnit = 'cm-1' | 'MHz'
type EnergyInfos = {[key in EnergyUnit]: EnergyLevels}
type Coefficients = ValueLabel<string>[]

interface BalanceDistributionOptions {

    label: string;
    collisionalTemp: number;
}

interface ComputeStatisticalWeightOptions {
    final: string;
    initial: string;
}

type VariableOptions = ReturnType<typeof window.persistentDB<{
    power: string;
    numberDensity: string;
    k3_branch: string;
}>>
