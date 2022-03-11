
import numpy as np
from scipy.special import voigt_profile

def generateNShapedProfile(N, method="lorentz", verbose=True, varyAll=False):
    gaussian = method=="gaussian"
    lorentz = method=="lorentz"
    voigt = method=="voigt"

    main_args = 'sigma, ' if gaussian or voigt  else ''
    main_args += 'gamma, ' if lorentz or voigt  else ''
    main_args += "*args"

    finalFn = f"def lineShape(x, {'*args' if varyAll else main_args}):\n"
    finalFn += f"\n\tdef getline(i):\n"
    
    if varyAll:
        finalFn += f"\n\t\tprofile = voigt_profile(x-FREQ[i]{', SIG[i]' if gaussian or voigt else ', 0'}{', GAM[i]' if lorentz or voigt else ', 0'})\n"
        finalFn += f"\t\tnormalised = profile/profile.max()\n"
        finalFn += f"\n\t\treturn AMPS[i]*normalised\n"
    else:
        sigma = 'sigma' if gaussian or voigt else 0
        gamma = 'gamma' if lorentz or voigt else 0
        finalFn += f"\n\t\tprofile = voigt_profile(x-FREQ[i], {sigma}, {gamma})\n"
        finalFn += f"\t\tnormalised = profile/profile.max()\n"
        finalFn += f"\n\t\treturn AMPS[i]**normalised\n"
    
    finalFn += "\n"

    finalFn += f"\t{N=}\n"
    finalFn += f"\tFREQ=args[-N:]\n"
    finalFn += f"\tAMPS=args[-2*N:-N]\n"

    if varyAll:
        if gaussian:
            finalFn += f"\tSIG=args[:N]\n"
        elif lorentz:
            finalFn += f"\tGAM=args[:N]\n"
        else:
            finalFn += f"\tSIG=args[:N]\n"
            finalFn += f"\tGAM=args[N:2*N]\n"
        
    finalFn += f"\n\tprofile = np.array([getline(i) for i in range(N)]).sum(axis=0)\n"
    finalFn += f"\n\treturn profile\n"
    
    if verbose: print(finalFn)
    exec(finalFn)
    return locals()["lineShape"]

    