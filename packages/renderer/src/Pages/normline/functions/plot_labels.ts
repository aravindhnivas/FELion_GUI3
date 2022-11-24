const signal = {
    rel: 'Signal = (1-C/B)*100',
    log: 'Signal = -ln(C/B)/Power(in J)',
    hv: 'Signal = -ln(C/B)/#Photons',
}
const set_title = (method: 'rel' | 'log' | 'hv') => {
    return `Normalised and Averaged Spectrum<br>${signal[method]}; {C=Measured Count, B=Baseline Count}`
}

export const plotlayout = {
    Relative: {
        title: set_title('rel'),
        yaxis: { title: 'Relative Depletion (%)' },
        xaxis: { title: 'Calibrated Wavelength (cm-1)' },
        key: 'average_rel',
    },
    Log: {
        title: set_title('log'),
        yaxis: { title: 'Normalised Intensity per J' },
        xaxis: { title: 'Calibrated Wavelength (cm-1)' },
        key: 'average',
    },
    IntensityPerPhoton: {
        title: set_title('hv'),
        yaxis: { title: 'Normalised Intensity per photon' },
        xaxis: { title: 'Calibrated Wavelength (cm-1)' },
        key: 'average_per_photon',
    },
}
