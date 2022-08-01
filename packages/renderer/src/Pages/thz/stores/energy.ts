import { derived, writable, get} from "svelte/store";
import { boltzmanConstantInMHz, boltzmanConstantInWavenumber, SpeedOfLight } from '$src/js/constants'
import { excitedFrom, excitedTo } from './common'
// import { tick } from "svelte";

export const numberOfLevels = writable<number>(2);
export const energyUnit = writable<EnergyUnit>('cm-1');
export const energyInfos = writable<EnergyInfos>({"cm-1": [], MHz: []});
export const energyLevels = derived([energyInfos, energyUnit], ([$energyInfos, $energyUnit]) => {
    return $energyInfos[$energyUnit]
});

const Boltzmann = {
    MHz: boltzmanConstantInMHz,
    'cm-1': boltzmanConstantInWavenumber,
}

export const kB = derived([energyUnit], ([$energyUnit]) => {
    return Boltzmann[$energyUnit]
});

export const get_KT = (T: number) => get(kB) * T

export const transitionFrequency = derived([excitedFrom, excitedTo], ([$excitedFrom, $excitedTo]) => {
    
    const lowerLevelEnergy = get(energyLevels).filter((energy) => energy.label == $excitedFrom)?.[0]?.value || 0
    const upperLevelEnergy = get(energyLevels).filter((energy) => energy.label == $excitedTo)?.[0]?.value || 0

    const frequency = upperLevelEnergy - lowerLevelEnergy
    if (get(energyUnit) === 'cm-1') {
        return frequency * SpeedOfLight * 1e2 * 1e-6
    }
    return frequency
});
