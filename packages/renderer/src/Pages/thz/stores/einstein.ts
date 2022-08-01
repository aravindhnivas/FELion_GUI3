import { writable } from "svelte/store";

export const einsteinCoefficientA = writable<Coefficients>([]);
export const einsteinCoefficientB = writable<Coefficients>([]);
export const einsteinCoefficientB_rateConstant = writable<Coefficients>([]);
