import {SpeedOfLight} from '$src/js/constants'

export const wavenumberToMHz = (energy: ValueLabel<number>) => ({
    ...energy,
    value: Number(energy.value * SpeedOfLight * 1e2 * 1e-6)
})

export const MHzToWavenumber = (energy: ValueLabel<number>) => ({
    ...energy,
    value: Number(energy.value / (SpeedOfLight * 1e2 * 1e-6))
})
