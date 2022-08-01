import { writable } from "svelte/store";

export const electronSpin = writable<boolean>(false);
export const zeemanSplit = writable<boolean>(false);

export const currentLocation = window.persistentDB<string>('ROSAA_currentLocation', '');
export const configFilename = writable<boolean>(false);

export const excitedTo = writable<string>('');
export const excitedFrom = writable<string>('');
export const trapTemp = writable<number>(5);