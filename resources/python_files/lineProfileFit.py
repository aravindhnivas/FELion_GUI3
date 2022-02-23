
import numpy as np
from uncertainties import unumpy as unp
from scipy.optimize import curve_fit
from scipy.special import voigt_profile

def fitData(freq, inten, fwhmParameter=[0.1], gaussianFit=False, voigtFit=False):
    '''
    Description:\n
        default: Lorentian profile\n
        freq should be in GHz which will be converted to MHz while fitting so fwhmParameter should be in MHz\n
    '''

    def fitProfile(x, x0, A, *args):

        _fwhmParameter = args if voigtFit else ([0, args], [args, 0])[gaussianFit] 

        profile = voigt_profile(x-x0, *_fwhmParameter)
        norm = profile/profile.max()
        normalisedProfile = A*norm

        return normalisedProfile
    
    freq *= 1000  # GHz --> MHz
    maxIntenInd = inten.argmax()
    amplitude = inten[maxIntenInd]
    cen = freq[maxIntenInd]

    p0=[cen, amplitude, *fwhmParameter]
    pop, pcov = curve_fit(fitProfile, freq, inten, p0=p0)
    perr = np.sqrt(np.diag(pcov))
    print(f"{pop=}\n{perr=}", flush=True)

    fittedY = fitProfile(freq, *pop)

    # MHz --> GHz
    freq /= 1000 

    pop[0] /= 1000
    perr[0] /= 1000

    pop[2] /= 1000
    perr[2] /= 1000
    
    if voigtFit:
        pop[3] /= 1000
        perr[3] /= 1000

    params = unp.uarray(pop, perr)
    return freq, fittedY, params