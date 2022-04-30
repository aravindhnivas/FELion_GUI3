import json
import traceback
from pathlib import Path as pt
from typing import Callable, Iterable
from matplotlib.axes import Axes
import numpy as np
from felionlib.utils import logger
from .utils.plot import plot_exp

from scipy.optimize import curve_fit
from scipy.integrate import solve_ivp
# from felionlib.utils.msgbox import MsgBox, MB_ICONERROR

from felionlib.utils.FELion_definitions import readCodeFromFile
from .utils.plotWidgets import make_widgets
from .utils.savedata import saveData
from .utils.sliderlog import Sliderlog
from felionlib.utils.felionQt import felionQtWindow

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

    rateCoefficientArgs = (
        [10**rate.val for rate in k3Sliders.values()],
        [10**rate.val for rate in kCIDSliders.values()],
    )
    dNdtSol = solve_ivp(compute_attachment_process, tspan, initialValues, method="Radau", t_eval=simulateTime).y
    for line, data in zip(fitPlot, dNdtSol):
        line.set_ydata(data)
    widget.blit.update()


k_fit, k_err = [], []


def saveDataFull():
    saveData(
        args, ratek3, k3Labels, kCIDLabels, k_fit, k_err, rateCoefficientArgs, fitPlot, expPlot, rateConstantsFileData
    )


def KineticMain():

    global initialValues, tspan, simulateTime, compute_attachment_process, checkboxes
    global kvalueLimits, rateCoefficientArgs, plotted, k3Sliders, kCIDSliders

    duration = expTime.max() * 1.2
    tspan = [0, duration]
    simulateTime = np.linspace(0, duration, 1000)
    location = pt(args["kineticEditorLocation"])
    filename = pt(location) / args["kineticEditorFilename"]

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
    )
    checkboxes = make_widgets(widget, fitfunc, saveDataFull, checkboxes)
    return


checkboxes = {"setbound": False}


def fitfunc() -> None:
    
    global k_fit, k_err
    k_err = []
    k_fit = []

    p0 = [*[10**rate.val for rate in k3Sliders.values()], *[10**rate.val for rate in kCIDSliders.values()]]

    if checkboxes["setbound"]:

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
    else:

        bounds = (
            [*[1e-33] * len(ratek3), *[1e-17] * len(ratekCID)],
            [*[1e-29] * len(ratek3), *[1e-14] * len(ratekCID)],
        )

    logger(f"{bounds=}")
    try:

        k_fit, kcov = curve_fit(
            fitODE,
            expTime,
            expData.flatten(),
            p0=p0,
            bounds=bounds
            # sigma=expDataError.flatten(), absolute_sigma=True,
        )
        k_err = np.sqrt(np.diag(kcov))
        logger(f"{k_fit=}\n{k_err=}")
        logger("fitted")

        for counter0, _k3 in enumerate(k3Sliders.values()):
            _k3.set_val(np.log10(k_fit[: len(ratek3)][counter0]))

        for counter1, _kCID in enumerate(kCIDSliders.values()):
            _kCID.set_val(np.log10(k_fit[len(ratek3) :][counter1]))
        print(f"{rateCoefficientArgs=}", flush=True)
    
    except Exception:
        k_fit = []
        k_err = []
        error = traceback.format_exc(5)
        
        print(f"{plotted=}\nerror while fitting data: \n{error=}", flush=True)

        if plotted:
            widget.showdialog("Error", error, type="critical")


fitPlot: list[Axes] = []
expPlot: list[Axes] = []

args = None
widget: felionQtWindow = None
savefile: pt = None
rateCoefficientArgs: tuple[np.ndarray, np.ndarray]  = ()


def main(arguments):
    global args, currentLocation, nameOfReactants, expTime, expData, expDataError, temp, rateConstantsFileData, numberDensity, totalAttachmentLevels, selectedFile, initialValues, k3Labels, kCIDLabels, ratek3, ratekCID, savedir, savefile, keyFoundForRate, data, widget

    args = arguments
    currentLocation = pt(args["currentLocation"]).parent

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
    savedir = currentLocation / "OUT"
    savefile = savedir / "k_fit.json"
    keyFoundForRate = False
    rateConstantsFileData = {}

    if savefile.exists():

        with open(savefile, "r") as f:

            keyFound = False
            rateConstantsFileContents = f.read()

            if len(rateConstantsFileContents) > 0:

                rateConstantsFileData = json.loads(rateConstantsFileContents)
                print(rateConstantsFileData, flush=True)

                keyFound = selectedFile in rateConstantsFileData
                print(f"{keyFound=}", flush=True)

            if keyFound:
                k3_fit_keyvalues = rateConstantsFileData[selectedFile]["k3_fit"]
                k3Labels = [key.strip() for key in k3_fit_keyvalues.keys()]
                ratek3 = np.array([float(value[0]) for value in k3_fit_keyvalues.values()])

                kCID_fit_keyvalues = rateConstantsFileData[selectedFile]["kCID_fit"]
                kCIDLabels = [key.strip() for key in kCID_fit_keyvalues.keys()]

                ratekCID = np.array([float(value[0]) for value in kCID_fit_keyvalues.values()])
                if len(args["ratek3"].split(",")) == len(k3Labels):
                    if len(args["ratekCID"].split(",")) == len(kCIDLabels):
                        keyFoundForRate = True
                else:
                    keyFoundForRate = False

    if not keyFoundForRate:
        k3Labels = [i.strip() for i in args["ratek3"].split(",")]
        kCIDLabels = [i.strip() for i in args["ratekCID"].split(",")]
        ratek3 = [float(args["k3Guess"]) for _ in k3Labels]
        ratekCID = [float(args["kCIDGuess"]) for _ in kCIDLabels]

    widget = felionQtWindow(title=f"kinetics : {selectedFile}",
                windowGeometry=(1200, 600), location=savedir, attachControlLayout=False)
    
    KineticMain()
    
    widget.ax.set_xbound(lower=-0.5)
    widget.ax.set_ybound(lower=1)
    
    widget.optimize_figure()
    widget.qapp.exec()
    