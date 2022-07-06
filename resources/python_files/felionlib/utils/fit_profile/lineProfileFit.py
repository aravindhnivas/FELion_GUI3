import numpy as np
from uncertainties import unumpy as unp, ufloat as uf
from scipy.optimize import curve_fit
from scipy.special import voigt_profile
from .generateNShapedProfile import generateNShapedProfile
import numpy.typing as npt

# from uncertainties.umath import math as umath

fitMethod = "lorentz"


def fitProfile(x, *args):
    A, *fwhmParameter, x0 = args

    if fitMethod == "gaussian":
        fwhmParameter = [fwhmParameter, 0]
    elif fitMethod == "lorentz":
        fwhmParameter = [0, fwhmParameter]

    profile = voigt_profile(x - x0, *fwhmParameter)
    norm = profile / profile.max()
    normalisedProfile = A * norm

    return normalisedProfile


def getInitialParams(paramsTable=[]):

    FREQ = []
    AMPS = []
    SIG = []
    GAM = []

    for params in paramsTable:

        params = {key: float(value) for key, value in params.items() if not key == "id"}
        FREQ.append(params["freq"])
        AMPS.append(params["amp"])

        sigma = params["fG"] / (2 * np.sqrt(2 * np.log(2)))
        SIG.append(sigma)

        gamma = params["fL"] / 2
        GAM.append(gamma)
    print(f"{FREQ=}\n{AMPS=}\n{SIG=}\n{GAM=}", flush=True)
    return FREQ, AMPS, SIG, GAM


def compute_fV(sigma, gamma):
    fL = 2 * gamma
    fG = compute_fG(sigma)
    return 0.5346 * fL + (0.2166 * fL**2 + fG**2) ** 0.5


def compute_fG(sigma):
    return 2 * (2 * np.log(2)) ** 0.5 * sigma


def fitData(
    freq: npt.NDArray[np.float64],
    inten: npt.NDArray[np.float64],
    method="lorentz",
    fitfile="",
    paramsTable=[],
    varyAll=False,
):

    """
    Description:\n
        freq<List> in GHz\n
        fwhmParameter<List> in MHz\n
    """

    global fitMethod
    fitMethod = method

    print(f"{method=}", flush=True)
    FREQ, AMPS, SIG, GAM = getInitialParams(paramsTable)

    N = len(FREQ)
    lineProfileFn = generateNShapedProfile(N, method=method, varyAll=varyAll, verbose=True)

    if varyAll:
        FWHMParams = [*SIG, *GAM] if method == "voigt" else (GAM, SIG)[method == "gaussian"]
        p0 = [*[_ / 1000 for _ in FWHMParams], *AMPS, *FREQ]

    else:
        FWHMParams = [SIG[0], GAM[0]] if method == "voigt" else ([GAM[0]], [SIG[0]])[method == "gaussian"]
        p0 = [*[_ / 1000 for _ in FWHMParams], *AMPS, *FREQ]

    print(f"{p0=}", flush=True)

    pop, pcov = curve_fit(lineProfileFn, freq, inten, p0=p0)

    perr = np.sqrt(np.diag(pcov))
    upop = unp.uarray(pop, perr)

    print(f"{upop=}", flush=True)
    fittedY = lineProfileFn(freq, *pop)
    fittedInfos = {"freq": freq, "fittedY": fittedY, "fitFunction": lineProfileFn}

    fittedParams = {"FREQ": upop[-N:], "AMPS": upop[-2 * N : -N]}

    if method == "voigt":
        fittedParams["SIG"] = upop[:N]
        fittedParams["GAM"] = upop[N : 2 * N]
    else:
        fittedParams["SIG" if method == "gaussian" else "GAM"] = upop[:N]
    print(f"{fittedParams=}", flush=True)

    fittedParamsTable = []
    counter = 0

    for frequency, amp in zip(fittedParams["FREQ"], fittedParams["AMPS"]):

        fitparams = {"filename": fitfile, "freq": f"{frequency*1000:.3f}", "amp": f"{amp:.2f}"}
        if method == "gaussian":
            sigma = fittedParams["SIG"][counter] * 1000
            fG = compute_fG(sigma)
            fitparams["sigma"] = f"{sigma:.3f}"
            fitparams["fwhm"] = f"{fG:.3f}"

        elif method == "lorentz":
            gamma = fittedParams["GAM"][counter] * 1000
            fitparams["gamma"] = f"{gamma:.3f}"
            fitparams["fwhm"] = f"{2*gamma:.3f}"

        elif method == "voigt":
            sigma = fittedParams["SIG"][counter] * 1000
            gamma = fittedParams["GAM"][counter] * 1000
            fitparams["sigma"] = f"{sigma:.3f}"
            fitparams["gamma"] = f"{gamma:.3f}"
            fV = compute_fV(sigma, gamma)
            fitparams["fwhm"] = f"{fV:.3f}"

        fittedParamsTable.append(fitparams)
        counter += 1

    return fittedParamsTable, fittedInfos
