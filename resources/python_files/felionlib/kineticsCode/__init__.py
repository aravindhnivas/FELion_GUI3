
import json
import traceback
from pathlib import Path as pt
import numpy as np
from .utils.definitions import log
from .utils.plot import plot_exp
from scipy.optimize import curve_fit
from scipy.integrate import solve_ivp
from felionlib.utils.FELion_widgets import FELion_Tk
from felionlib.utils.msgbox import MsgBox, MB_ICONERROR
from felionlib.utils.FELion_definitions import readCodeFromFile

from tkinter.messagebox import showerror


def fitODE(t, *args):

    global rateCoefficientArgs

    tspan = [0, t.max()*1.2]
    rateCoefficientArgs = (args[:len(ratek3)], args[len(ratek3):])

    dNdtSol = solve_ivp(
        compute_attachment_process, tspan, initialValues,
        method="Radau", t_eval=t
    ).y
    return dNdtSol.flatten()


tspan = None
simulateTime = None
kvalueLimits = {}
compute_attachment_process = None


def codeToRun(code):
    exec(code)
    return locals()


def update(val=None):

    global rateCoefficientArgs

    rateCoefficientArgs = (
        [10**rate.val for rate in k3Sliders.values()],
        [10**rate.val for rate in kCIDSliders.values()]
    )

    dNdtSol = solve_ivp(
        compute_attachment_process, tspan, initialValues,
        method="Radau", t_eval=simulateTime
    ).y

    for line, data in zip(fitPlot, dNdtSol):
        line.set_ydata(data)

    widget.canvas.draw_idle()


def KineticMain():

    global initialValues, tspan, simulateTime,\
        compute_attachment_process, kvalueLimits, \
        k3Sliders, kCIDSliders, toggleLine, rateCoefficientArgs

    duration = expTime.max()*1.2
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

    k3Sliders, kCIDSliders, toggleLine = plot_exp(
        compute_attachment_process, widget,
        k3Labels, kCIDLabels, ratek3, ratekCID, kvalueLimits,
        keyFoundForRate, update, expPlot, fitPlot, args,
        fitfunc, k_fit, k_err, rateCoefficientArgs, rateConstantsFileData
    )

    return


k_err = []
k_fit = []


def fitfunc(event=None):

    global k_fit, k_err

    p0 = [
        *[10**rate.val for rate in k3Sliders.values()],
        *[10**rate.val for rate in kCIDSliders.values()]
    ]

    if checkboxes["setbound"]:

        ratio = 0.1

        bounds = (
            [
                *[
                    np.format_float_scientific(
                        10**(rate.val-ratio),
                        precision=2
                    ) for rate in k3Sliders.values()
                ],
                *[
                    np.format_float_scientific(
                        10**(rate.val-ratio),
                        precision=2
                    ) for rate in kCIDSliders.values()
                ]
            ],
            [
                *[
                    np.format_float_scientific(
                        10**(rate.val+ratio),
                        precision=2
                    ) for rate in k3Sliders.values()
                ],
                *[
                    np.format_float_scientific(
                        10**(rate.val+ratio),
                        precision=2
                    ) for rate in kCIDSliders.values()
                ]
            ]
        )
    else:

        bounds = (
            [*[1e-33]*len(ratek3), *[1e-17]*len(ratekCID)],
            [*[1e-29]*len(ratek3), *[1e-14]*len(ratekCID)]
        )

    log(f"{bounds=}")

    try:
        k_fit, kcov = curve_fit(
            fitODE, expTime, expData.flatten(),
            p0=p0, sigma=expDataError.flatten(),
            absolute_sigma=True, bounds=bounds
        )

        k_err = np.sqrt(np.diag(kcov))

        log(f"{k_fit=}\n{k_err=}")
        log("fitted")

        for counter0, _k3 in enumerate(k3Sliders.values()):
            _k3.set_val(np.log10(k_fit[:len(ratek3)][counter0]))

        for counter1, _kCID in enumerate(kCIDSliders.values()):
            _kCID.set_val(np.log10(k_fit[len(ratek3):][counter1]))

    except Exception:

        k_fit = []
        k_err = []
        if plotted:
            MsgBox("Error", traceback.format_exc(), MB_ICONERROR)


fitPlot = []
expPlot = []
plotted = False
checkboxes = {
    "setbound": False
}
toggleLine = {}

args = None
widget = None
savefile = None
k3Sliders = {}
kCIDSliders = {}
rateCoefficientArgs = ()


def main(arguments):

    global args, currentLocation, nameOfReactants, \
        expTime, expData, expDataError, temp, rateConstantsFileData,\
        numberDensity, totalAttachmentLevels, selectedFile, initialValues, \
        k3Labels, kCIDLabels, ratek3, ratekCID, savedir, savefile, \
        keyFoundForRate, data, widget

    args = arguments
    currentLocation = pt(args["currentLocation"]).parent

    data = args["data"]
    nameOfReactants = args["nameOfReactantsArray"]

    expTime = np.array(
        data[nameOfReactants[0]]["x"],
        dtype=float
    )*1e-3  # ms --> s

    expData = np.array(
        [data[name]["y"] for name in nameOfReactants],
        dtype=float
    )

    expDataError = np.array(
        [
            data[name]["error_y"]["array"]
            for name in nameOfReactants
        ],
        dtype=float
    )

    temp = float(args["temp"])
    selectedFile = args["selectedFile"]

    numberDensity = float(args["numberDensity"])
    initialValues = [float(i) for i in args["initialValues"]]

    totalAttachmentLevels = len(initialValues)-1
    savedir = currentLocation/"OUT"
    savefile = savedir/"k_fit.json"
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
                ratek3 = np.array(
                    [float(value[0]) for value in k3_fit_keyvalues.values()]
                )

                kCID_fit_keyvalues = rateConstantsFileData[selectedFile]["kCID_fit"]
                kCIDLabels = [key.strip() for key in kCID_fit_keyvalues.keys()]

                ratekCID = np.array(
                    [float(value[0]) for value in kCID_fit_keyvalues.values()]
                )

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

    
    try:
        widget = FELion_Tk(title=f"Kinetics: {selectedFile}", location=savedir)
        
        KineticMain()
        widget.mainloop()

    except:
        showerror("ERROR", traceback.format_exc(5))
        widget.destroy()
