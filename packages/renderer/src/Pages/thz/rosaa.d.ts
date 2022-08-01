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
    // energyLevels: EnergyLevels;
    collisionalTemp: number;
    // electronSpin: boolean;
    // zeemanSplit: boolean;
    // energyUnit: EnergyUnit;
}

interface ComputeStatisticalWeightOptions {
    // electronSpin: boolean;
    // zeemanSplit: boolean;
    final: string;
    initial: string;
}

interface BoltzmanDistributionOptions {
    // energyLevels: EnergyLevels;
    trapTemp: number;
    // electronSpin: boolean;
    // zeemanSplit: boolean;
    // energyUnit: EnergyUnit;
}