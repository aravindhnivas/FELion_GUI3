import { derived, writable, get} from "svelte/store";
import { boltzmanConstantInMHz, boltzmanConstantInWavenumber } from '$src/js/constants'

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
