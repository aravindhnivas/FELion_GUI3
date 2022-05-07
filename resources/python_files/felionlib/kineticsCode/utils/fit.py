import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import solve_ivp
from felionlib.utils import logger

from felionlib.kineticsCode.utils.plot import fitPlot
from felionlib.kineticsCode import (
    expTime, expData, expDataError, widget, initialValues, tspan, 
    simulateTime, kinetics_equation_file, numberDensity # numberDensity is important for the fit
)
from felionlib.kineticsCode.utils.widgets.checkboxes import checkboxes
from .configfile import ratek3, ratekCID, k_err as k_err_config

from felionlib.utils.FELion_definitions import readCodeFromFile
from felionlib.kineticsCode.utils.rateSliders import k3Sliders, kCIDSliders, update_sliders


k_fit = []
k_err = k_err_config
rateCoefficientArgs: tuple[np.ndarray, np.ndarray] = (ratek3, ratekCID)


def codeToRun(code: str):
    exec(code)
    return locals()

codeContents = readCodeFromFile(kinetics_equation_file)
codeOutput = codeToRun(codeContents)
compute_attachment_process = codeOutput["compute_attachment_process"]
print(f"{compute_attachment_process=}", flush=True)


if "kvalueLimits" in codeOutput:
    kvalueLimits = codeOutput["kvalueLimits"]
    print(f"{kvalueLimits=}", flush=True)
    

def intialize_fit_plot() -> None:
    dNdtSol: np.ndarray = solve_ivp(
        compute_attachment_process,
        tspan,
        initialValues,
        method="Radau",
        t_eval=simulateTime,
    ).y
    return dNdtSol

def update(val: float = None):
    
    global rateCoefficientArgs
    
    try:
        rateCoefficientArgs = (
            [10**rate.val for rate in k3Sliders.values()],
            [10**rate.val for rate in kCIDSliders.values()],
        )
        dNdtSol = solve_ivp(compute_attachment_process, tspan, initialValues, method="Radau", t_eval=simulateTime).y
        for line, data in zip(fitPlot, dNdtSol):
            line.set_ydata(data)
        widget.blit.update()
    except Exception:
        widget.showErrorDialog()
        

def fitODE(t: np.ndarray, *args):
    global rateCoefficientArgs
    tspan = [0, t.max() * 1.2]
    rateCoefficientArgs = (args[: len(ratek3)], args[len(ratek3) :])
    dNdtSol: np.ndarray = solve_ivp(compute_attachment_process, tspan, initialValues, method="Radau", t_eval=t).y
    return dNdtSol.flatten()



def fit_kinetic_data() -> None:
    
    global k_fit, k_err

    setbound = checkboxes['set_bound']
    includeError = checkboxes['include_error']
    logger(f"{checkboxes=}")
    
    p0 = [*[10**rate.val for rate in k3Sliders.values()], *[10**rate.val for rate in kCIDSliders.values()]]
    bounds = (-np.inf, np.inf)
    
    if setbound:
        ratio = 0.1
        bounds = (
            [
                *[np.format_float_scientific(10 ** (rate.val - ratio), precision=2) for rate in k3Sliders.values()],
                *[np.format_float_scientific(10 ** (rate.val - ratio), precision=2) for rate in kCIDSliders.values()],
            ],
            [
                *[np.format_float_scientific(10 ** (rate.val + ratio), precision=2) for rate in k3Sliders.values()],
                *[np.format_float_scientific(10 ** (rate.val + ratio), precision=2) for rate in kCIDSliders.values()],
            ],
        )
    logger(f"{bounds=}")
    try:
        
        k_fit, kcov = curve_fit(
            fitODE, expTime, expData.flatten(), p0=p0, bounds=bounds,
            sigma= expDataError.flatten() if includeError else None, absolute_sigma=includeError,
        )
        
        k_err = np.sqrt(np.diag(kcov))
        # if not np.all(np.isfinite(k_err)):
        #     raise Exception("Error: Non-finite error values")
        
        logger(f"{k_fit=}\n{kcov=}\n{k_err=}")
        logger("fitted")
        
        update_sliders(k_fit[: len(ratek3)], k_fit[len(ratek3) :])

    except Exception as err:
        from felionlib.kineticsCode import plotted
        if plotted:
            widget.showErrorDialog()
            