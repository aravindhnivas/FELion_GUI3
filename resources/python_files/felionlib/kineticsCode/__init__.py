import json
from pathlib import Path as pt
from typing import Callable, Iterable
from matplotlib.axes import Axes
import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import solve_ivp

from .utils.plot import plot_exp
from .utils.savedata import saveData
from .utils.sliderlog import Sliderlog
from .utils.plotWidgets import make_widgets

from felionlib.utils import logger
from felionlib.utils.felionQt import felionQtWindow
from felionlib.utils.FELion_definitions import readCodeFromFile
from .utils.widgets.checkboxes import checkboxes


def fitODE(t: np.ndarray, *args):
    global rateCoefficientArgs
    tspan = [0, t.max() * 1.2]
    rateCoefficientArgs = (args[: len(ratek3)], args[len(ratek3) :])
    dNdtSol: np.ndarray = solve_ivp(compute_attachment_process, tspan, initialValues, method="Radau", t_eval=t).y
    return dNdtSol.flatten()


tspan: Iterable = None
simulateTime: np.ndarray = None
kvalueLimits: dict[str, float] = {}
compute_attachment_process: bool = None
k3Sliders: dict[str, Sliderlog] = {}
kCIDSliders: dict[str, Sliderlog] = {}


def codeToRun(code: str) -> Callable:
    exec(code)
    return locals()


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

k_fit, k_err = [], []


def saveDataFull():
    
    saveData(
        args,
        ratek3,
        k3Labels,
        kCIDLabels,
        k_err,
        rateCoefficientArgs,
        fitPlot,
        expPlot,
        rateConstantsFileData,
        savefile=fit_config_file,
    )


def KineticMain():

    global initialValues, tspan, simulateTime, compute_attachment_process
    global kvalueLimits, rateCoefficientArgs, plotted, k3Sliders, kCIDSliders

    duration = expTime.max() * 1.2
    tspan = [0, duration]
    simulateTime = np.linspace(0, duration, 1000)

    filename = kinetic_file_location / args["kineticEditorFilename"]

    codeContents = readCodeFromFile(filename)
    codeOutput = codeToRun(codeContents)

    rateCoefficientArgs = (ratek3, ratekCID)
    compute_attachment_process = codeOutput["compute_attachment_process"]
    if "kvalueLimits" in codeOutput:
        kvalueLimits = codeOutput["kvalueLimits"]
        print(f"{kvalueLimits=}", flush=True)

    plotted = False

    plotted, k3Sliders, kCIDSliders = plot_exp(
        compute_attachment_process,
        widget,
        k3Labels,
        kCIDLabels,
        ratek3,
        ratekCID,
        kvalueLimits,
        keyFoundForRate,
        update,
        expPlot,
        fitPlot,
        args,
        fitfunc,
        kinetic_plot_adjust_configs_obj,
    )
    
    make_widgets()
    return


def fitfunc() -> None:
    
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
        if not np.all(np.isfinite(k_err)):
            raise Exception("Error: Non-finite error values")
        logger(f"{k_fit=}\n{kcov=}\n{k_err=}")
        logger("fitted")

        for counter0, _k3 in enumerate(k3Sliders.values()):
            _k3.set_val(np.log10(k_fit[: len(ratek3)][counter0]))

        for counter1, _kCID in enumerate(kCIDSliders.values()):
            _kCID.set_val(np.log10(k_fit[len(ratek3) :][counter1]))
            
        print(f"{rateCoefficientArgs=}", flush=True)

    except Exception:
        if plotted:
            widget.showErrorDialog()


fitPlot: list[Axes] = []
expPlot: list[Axes] = []
args = None
widget: felionQtWindow = None
rateCoefficientArgs: tuple[np.ndarray, np.ndarray] = ()
fit_config_file: pt = None

kinetic_plot_adjust_configs_obj: dict[str, float] = {}


def main(arguments):
    global args, kinetic_file_location, nameOfReactants, expTime, expData, kinetic_plot_adjust_configs_obj
    global expDataError, temp, rateConstantsFileData, numberDensity
    global totalAttachmentLevels, selectedFile, initialValues
    global k3Labels, kCIDLabels, ratek3, ratekCID, k_err
    global keyFoundForRate, data, widget, fit_config_file

    args = arguments
    kinetic_file_location = pt(args["kinetic_file_location"])
    config_files_location = kinetic_file_location.parent / "configs"

    if not config_files_location.exists():
        config_files_location.mkdir()

    data = args["data"]
    nameOfReactants = args["nameOfReactantsArray"]

    expTime = np.array(data[nameOfReactants[0]]["x"], dtype=float) * 1e-3  # ms --> s

    expData = np.array([data[name]["y"] for name in nameOfReactants], dtype=float)

    expDataError = np.array([data[name]["error_y"]["array"] for name in nameOfReactants], dtype=float)

    temp = float(args["temp"])
    selectedFile = args["selectedFile"]

    numberDensity = float(args["numberDensity"])
    initialValues = [float(i) for i in args["initialValues"]]

    totalAttachmentLevels = len(initialValues) - 1
    outdir = kinetic_file_location.parent / "OUT"

    fit_config_file = config_files_location / args["$fit_config_filename"]
    keyFoundForRate = False
    rateConstantsFileData = {}

    # print(f"{fit_config_file=}", flush=True)
    k3Labels = [i.strip() for i in args["ratek3"].split(",")]
    kCIDLabels = [i.strip() for i in args["ratekCID"].split(",")]
    
    ratek3 = [float(args["k3Guess"]) for _ in k3Labels]
    ratekCID = [float(args["kCIDGuess"]) for _ in kCIDLabels]
    k3_err = [0]*len(ratek3)
    kCID_err = [0]*len(ratekCID)
    
    if fit_config_file.exists():
    
        with open(fit_config_file, "r") as f:

            keyFound = False
            rateConstantsFileContents = f.read()

            if len(rateConstantsFileContents) > 0:

                rateConstantsFileData = json.loads(rateConstantsFileContents)
                print(rateConstantsFileData, flush=True)

                keyFound = selectedFile in rateConstantsFileData
                print(f"{keyFound=}", flush=True)

            if keyFound:

                k3_fit_keyvalues: dict[str, float] = rateConstantsFileData[selectedFile]["k3_fit"]
                kCID_fit_keyvalues: dict[str, float] = rateConstantsFileData[selectedFile]["kCID_fit"]
                
                for k3_key in k3_fit_keyvalues.keys():
                    
                    if k3_key in k3Labels:
                        k3_found_index = k3Labels.index(k3_key)
                        ratek3[k3_found_index] = float(k3_fit_keyvalues[k3_key][0])
                        k3_err[k3_found_index] = float(k3_fit_keyvalues[k3_key][1])
                        
                        keyFoundForRate = True
                        
                for kCID_key in kCID_fit_keyvalues.keys():
                    
                    if kCID_key in kCIDLabels:
                        kCID_found_index = kCIDLabels.index(kCID_key)
                        ratekCID[kCID_found_index] = float(kCID_fit_keyvalues[kCID_key][0])
                        kCID_err[kCID_found_index] = float(kCID_fit_keyvalues[kCID_key][1])
                        keyFoundForRate = True
                
    k_err = np.concatenate((k3_err, kCID_err))
    print(f"{k_err=}", flush=True)
    
    kinetic_plot_adjust_configs_obj = {
        key: float(value) for key, value in args["kinetic_plot_adjust_configs_obj"].items()
    }
    if not kinetic_plot_adjust_configs_obj:
        kinetic_plot_adjust_configs_obj = {"right": 0.570, "top": 0.900, "left": 0.120, "bottom": 0.160}

    widget = felionQtWindow(
        title=f"kinetics : {selectedFile}", windowGeometry=(1200, 600), location=outdir, attachControlLayout=False
    )

    KineticMain()

    widget.ax.set_xbound(lower=-0.5)
    widget.ax.set_ybound(lower=1)

    widget.optimize_figure()
    widget.toggle_controller_layout()

    widget.qapp.exec()
