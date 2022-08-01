import { derived, writable } from "svelte/store";

export const electronSpin = writable<boolean>(false);
export const zeemanSplit = writable<boolean>(false);

export const configFile = writable(<string>window.db.get('ROSAA_configfile') ?? '')

export const currentLocation = derived(configFile, ($configFile) => {
    if(!window.fs.isFile($configFile)) return ''
    window.db.set('ROSAA_configfile', $configFile)
    return window.path.dirname($configFile)
});

export const excitedTo = writable<string>('');
export const excitedFrom = writable<string>('');
export const trapTemp = writable<number>(5);