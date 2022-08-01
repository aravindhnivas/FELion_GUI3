import { derived, writable } from "svelte/store";

export const collisionalRates = writable<Coefficients>([])
export const collisionalCoefficient = writable<Coefficients>([])
export const collisionalCoefficient_balance = writable<Coefficients>([])

export const collisionalRateConstants = derived(
    [collisionalCoefficient, collisionalCoefficient_balance],
    ([$collisionalCoefficient, $collisionalCoefficient_balance]) => {
    return [...$collisionalCoefficient, ...$collisionalCoefficient_balance]
})
