import {SpeedOfLight} from '$src/js/constants'

export const wavenumberToMHz = (energy) => ({
    ...energy,
    value: Number(energy.value * SpeedOfLight * 1e2 * 1e-6).toFixed(3),
})

export const MHzToWavenumber = (energy) => ({
    ...energy,
    value: Number(energy.value / (SpeedOfLight * 1e2 * 1e-6)).toFixed(3),
})
