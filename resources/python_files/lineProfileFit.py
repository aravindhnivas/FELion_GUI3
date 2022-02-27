
import numpy as np
from uncertainties import unumpy as unp, ufloat as uf
from scipy.optimize import curve_fit
from scipy.special import voigt_profile
from generateNShapedProfile import generateNShapedProfile


fitMethod = "lorentz"

def fitProfile(x, *args):
        A, *fwhmParameter, x0 = args
       
        if fitMethod == "gaussian":
            fwhmParameter = [fwhmParameter, 0]
        elif fitMethod == "lorentz":
            fwhmParameter = [0, fwhmParameter]

        profile = voigt_profile(x-x0, *fwhmParameter)
        norm = profile/profile.max()
        normalisedProfile = A*norm

        return normalisedProfile

def getInitialParams(paramsTable=[]):
    FREQ = []
    AMPS = []
    SIG = []
    GAM = []

    for params in paramsTable:
        params = {key: float(value) for key, value in params.items() if not key=="id"}
        FREQ.append(params["freq"])
        AMPS.append(params["amp"])

        FG = params["fG"]
        computedSig = FG/(2*np.sqrt(2*np.log(2)))
        SIG.append(computedSig)
        
        FL = params["fL"]
        computedGam = FL/2
        GAM.append(computedGam)
    print(f"{FREQ=}\n{AMPS=}\n{SIG=}\n{GAM=}", flush=True)
    return FREQ, AMPS, SIG, GAM

def fitData(freq, inten, method="lorentz", fitfile="", paramsTable=[], varyAll=False):

    '''
    Description:\n
        freq<List> in GHz\n
        fwhmParameter<List> in MHz\n
    '''

    global fitMethod
    fitMethod = method

    print(f"{method=}", flush=True)

    FREQ, AMPS, SIG, GAM = getInitialParams(paramsTable)
    N = len(FREQ)

    lineProfileFn = generateNShapedProfile(
        N, method=method, varyAll=varyAll, verbose=True
    )

    if varyAll:
    
        FWHMParams = [*SIG, *GAM] if method=="voigt" else (GAM, SIG)[method=="gaussian"]
        p0=[*[_/1000 for _ in FWHMParams], *AMPS, *FREQ]
    else:
        FWHMParams = [SIG[0], GAM[0]] if method=="voigt" else ([GAM[0]], [SIG[0]])[method=="gaussian"]
        p0=[*[_/1000 for _ in FWHMParams], *AMPS, *FREQ]

    print(f"{p0=}", flush=True)
    pop, pcov = curve_fit(lineProfileFn, freq, inten, p0=p0)

    perr = np.sqrt(np.diag(pcov))
    upop = unp.uarray(pop, perr)
    
    print(f"{upop=}", flush=True)

    fittedY = lineProfileFn(freq, *pop)
    fittedInfos = {
        "freq": freq,
        "fittedY": fittedY,
        "fitFunction": lineProfileFn
    }

    fittedParams = {
        "FREQ": upop[-N:],
        "AMPS": upop[-2*N:-N]
    }
    

    if method=="voigt":

        fittedParams["SIG"] = upop[:N]
        fittedParams["GAM"] = upop[N:2*N]
    else:
        fittedParams["SIG" if method=="gaussian" else "GAM"] = upop[:N]

    print(f"{fittedParams=}", flush=True)

    fittedParamsTable = []
    counter = 0

    for frequency, amp in zip(fittedParams["FREQ"], fittedParams["AMPS"]):
        fitparams = {
            "filename": fitfile,
            "freq": f"{frequency*1000:.3f}",
            "amp": f"{amp:.2f}"
        }

        if method=="gaussian":
            fitparams["fG"] = f"{fittedParams['SIG'][counter]*1000:.3f}"
        if method=="lorentz":
            fitparams["fL"] = f"{fittedParams['GAM'][counter]*1000:.3f}"
        if method=="voigt":
            fitparams["fG"] = f"{fittedParams['SIG'][counter]*1000:.3f}"
            fitparams["fL"] = f"{fittedParams['GAM'][counter]*1000:.3f}"

        fittedParamsTable.append(fitparams)
        counter += 1

    return fittedParamsTable, fittedInfos
