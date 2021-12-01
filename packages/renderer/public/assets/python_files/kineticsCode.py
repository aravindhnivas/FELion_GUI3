
import sys, json, os
from pathlib import Path as pt
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from optimizePlot import optimizePlot
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox, CheckButtons
from scipy.optimize import curve_fit
from scipy.integrate import solve_ivp

main_module_loc = str(pt(__file__).joinpath("../../"))
sys.path.insert(0, main_module_loc)
from FELion_constants import pltColors
from FELion_definitions import readCodeFromFile

from msgbox import MsgBox, MB_ICONERROR, MB_ICONINFORMATION


# from functools import reduce
def log(msg): print(msg, flush=True)

class Sliderlog(Slider):

    """Logarithmic slider.
    Takes in every method and function of the matplotlib's slider.
    Set slider to *val* visually so the slider still is lineat but display 10**val next to the slider.
    Return 10**val to the update function (func)"""

    def set_val(self, val):

        xy = self.poly.xy
        if self.orientation == 'vertical':
            xy[1] = 0, val
            xy[2] = 1, val
        else:
            xy[2] = val, 1
            xy[3] = val, 0
        self.poly.xy = xy
        self.valtext.set_text(self.valfmt % 10**val)   # Modified to display 10**val instead of val
        if self.drawon:
            self.ax.figure.canvas.draw_idle()
        self.val = val
        if not self.eventson:
            return
        for cid, func in self.observers.items():
                func(10**val)

def codeToRun(code):
    exec(code)
    return locals()


def fitODE(t, *args):

    global rateCoefficientArgs
    tspan = [0, t.max()*1.2]
    
    rateCoefficientArgs=(args[:len(ratek3)], args[len(ratek3):])

    dNdt = solve_ivp(compute_attachment_process, tspan, initialValues, dense_output=True)
    dNdtSol = dNdt.sol(t)
    return dNdtSol.flatten()

tspan = None
simulateTime = None

compute_attachment_process = None
kvalueLimits = {}

def KineticMain():
    global initialValues, tspan, simulateTime, compute_attachment_process, kvalueLimits

    duration = expTime.max()*1.2
    tspan = [0, duration]
    simulateTime = np.linspace(0, duration, 1000)

    location = pt(args["kineticEditorLocation"])
    filename = pt(location) / args["kineticEditorFilename"]
    codeContents = readCodeFromFile(filename)
    codeOutput = codeToRun(codeContents)

    compute_attachment_process = codeOutput["compute_attachment_process"]
    if "kvalueLimits" in codeOutput:
        kvalueLimits = codeOutput["kvalueLimits"]
        print(f"{kvalueLimits=}", flush=True)
    
    # plot_exp_fn = profile_line(plot_exp)
    # plot_exp_fn()
    plot_exp()
    return

def formatArray(arr, precision=2):
    return [np.format_float_scientific(value, precision=precision) for value in arr]

k_err = []

def fitfunc(event=None):

    global k_err

    p0 = [*[10**rate.val for rate in k3Sliders.values()], *[10**rate.val for rate in kCIDSliders.values()]]

    log(f"{p0=}")

    if checkboxes["setbound"]:
        ratio = 0.1
        bounds=(
            [
                *[np.format_float_scientific(10**(rate.val-ratio), precision=2) for rate in k3Sliders.values()], 
                *[np.format_float_scientific(10**(rate.val-ratio), precision=2) for rate in kCIDSliders.values()]
            ],
            [
                *[np.format_float_scientific(10**(rate.val+ratio), precision=2) for rate in k3Sliders.values()],
                *[np.format_float_scientific(10**(rate.val+ratio), precision=2) for rate in kCIDSliders.values()]
            ]
        )
    else:
        bounds=([*[1e-33]*len(ratek3), *[1e-17]*len(ratekCID)], [*[1e-29]*len(ratek3), *[1e-14]*len(ratekCID)])
    
    log(f"{bounds=}")

    try:
    
        k_fit, kcov = curve_fit(fitODE, expTime, expData.flatten(),
            p0=p0, sigma=expDataError.flatten(), absolute_sigma=True, bounds=bounds   
        )

        k_err = np.sqrt(np.diag(kcov))
        log(f"{k_fit=}\n{k_err=}")
        log("fitted")
        
        for counter0, _k3 in enumerate(k3Sliders.values()):
            _k3.set_val(np.log10(k_fit[:len(ratek3)][counter0]))
        for counter1, _kCID in enumerate(kCIDSliders.values()):
            _kCID.set_val(np.log10(k_fit[len(ratek3):][counter1]))

        
        # saveData(None, k_fit, k_err)

    except Exception as error:
        error = f"Error occured while fitting: \n{error}"
        log(error)
        # k_err = []
        if plotted: MsgBox("Error", error, MB_ICONERROR)

def saveData(event, k_fit=None):

    try:
        savedir = currentLocation/"OUT"

        if not savedir.exists():
            os.mkdir(savedir)
        
        savefile = savedir/"k_fit.json"

        dataToSave = {}

        if savefile.exists():
        
            data = []
            with open(savefile, "r") as f:
                data = f.read()
                if data:
                    dataToSave = json.loads(data)


        with open(savefile, "w+") as f:

            if event:
                k_fit = [formatArray(rateCoefficientArgs[0]), formatArray(rateCoefficientArgs[1])]
            else:
                k_fit = [formatArray(k_fit[:len(ratek3)]), formatArray(k_fit[len(ratek3):])]

            if len(k_err)>0:
                k_err_format = [formatArray(k_err[:len(ratek3)]), formatArray(k_err[len(ratek3):])]
            else: k_err_format = None

            dataToSave[selectedFile] = {
                "k_fit": k_fit,
                "k_err": k_err_format, 
                "temp": f"{temp:.1f}", 
                "numberDensity": f"{numberDensity:.2e}"
            }
            data = json.dumps(dataToSave, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(data)

            log(f"file written: {savefile.name} in {currentLocation} folder")
            if plotted: 
                MsgBox("Saved", f"Rate constants written in json format : '{savefile.name}'\nLocation: {currentLocation}", MB_ICONINFORMATION)
            fig.savefig(f"{savedir/selectedFile}_.png", dpi=200)
    except Exception as error:
        if plotted: MsgBox("Error occured: ", f"Error occured while saving the file\n{error}", MB_ICONERROR)
        log(f"Error occured while saving the file\n{error}")

fig = None
ax = None

fitPlot = []
plotted=False
def ChangeYScale(yscale):
    ax.set_yscale(yscale)
    if yscale == "log":
        ax.set_ylim(ymin=0.1)
    fig.canvas.draw_idle()

def setNumberDensity(val):
    global numberDensity
    numberDensity = float(val)
    log(f"{numberDensity=}")

    ax.set_title(f"{selectedFile}: {temp:.1f} K {numberDensity:.2e}"+"$cm^{-3}$")
    fitfunc()

checkboxes = {
    "setbound": False
}


def checkboxesFunc(label):
    global checkboxes
    checkboxes[label] = not checkboxes[label]
    fig.canvas.draw_idle()

def plot_exp():

    global data, fig, ax, k3Sliders, kCIDSliders, rateCoefficientArgs

    fig, ax = plt.subplots(figsize=(12, 6))

    plt.subplots_adjust(right=0.6, top=0.95, left=0.09, bottom=0.25)
    
    axcolor = 'lightgoldenrodyellow'
    k3Sliders, kCIDSliders = make_slider(ax, axcolor)
    left, bottom, width, height = 0.1, 0.05, 0.1, 0.05
    
    rax = plt.axes([left, bottom, width, height], facecolor=axcolor)
    radio = RadioButtons(rax, ('log', 'linear'), active=0)
    radio.on_clicked(ChangeYScale)

    left += width+0.01
    buttonAxes = plt.axes([left, bottom, width, height], facecolor=axcolor)
    button = Button(buttonAxes, 'Fit', color=axcolor, hovercolor='0.975')
    button.on_clicked(fitfunc)

    left += width+0.01
    checkAxes = plt.axes([left, bottom, width, height], facecolor=axcolor)
    checkbox = CheckButtons(checkAxes, ("setbound", ), list(checkboxes.values()))
    
    checkbox.on_clicked(checkboxesFunc)

    left += width+0.01

    saveButtonAxes = plt.axes([left, bottom, width, height], facecolor=axcolor)
    saveButton = Button(saveButtonAxes, 'saveData', color=axcolor, hovercolor='0.975')
    saveButton.on_clicked(saveData)

    numberDensityWidgetAxes = plt.axes([0.9-width, bottom, width, height], facecolor=axcolor)
    numberDensityWidget = TextBox(numberDensityWidgetAxes, 'Number density', initial=f"{numberDensity:.2e}")
    numberDensityWidget.on_submit(setNumberDensity)

    for counter, key in enumerate(data.keys()):
        time = data[key]["x"]

        counts = data[key]["y"]
        error = data[key]["error_y"]["array"]
        ax.errorbar(time, counts, error, fmt=".", ms=10, label=key, c=pltColors[counter])

    ax = optimizePlot(ax, xlabel="Time (ms)", ylabel="Counts", yscale="log")
    # if yscale == "log":
    ax.set_ylim(ymin=0.1)
    # log(f"{temp=}")
    ax.set_title(f"{selectedFile}: @{temp:.1f} K {numberDensity:.2e}"+"$cm^{-3}$")

    rateCoefficientArgs=(ratek3, ratekCID)
    
    log(f"{rateCoefficientArgs=}")
    log(f"{initialValues=}")

    # return

    dNdt = solve_ivp(compute_attachment_process, tspan, initialValues, dense_output=True)
    log(f"{dNdt=}")
    # return
    dNdtSol = dNdt.sol(simulateTime)

    for counter, data in enumerate(dNdtSol):
        _fitPlot, = ax.plot(simulateTime*1e3, data, "-", c=pltColors[counter])
        fitPlot.append(_fitPlot)

    legend = ax.legend([f"${_}$" for _ in nameOfReactants])
    legend.set_draggable(True)

    try:
        global plotted
        if numberDensity > 0 and not keyFoundForRate:
            fitfunc()
        plotted = True

    except Exception as error:
        log(error)
    # plt.show()
    
rateCoefficientArgs = ()

def update(val=None):

    global rateCoefficientArgs
    
    rateCoefficientArgs=(
    
        [10**rate.val for rate in k3Sliders.values()], 
        [10**rate.val for rate in kCIDSliders.values()]
    )
    
    dNdt = solve_ivp(compute_attachment_process, tspan, initialValues, dense_output=True)

    dNdtSol = dNdt.sol(simulateTime)
    for line, data in zip(fitPlot, dNdtSol):
        line.set_ydata(data)
    
    fig.canvas.draw_idle()


# update = profile_line(fitData)

k3Sliders = {}
kCIDSliders = {}

def make_slider(ax, axcolor):

    global k3Sliders, kCIDSliders

    ax.margins(x=0)
    
    height = 0.03
    width = 0.25
    bottom = 0.9


    counter = 0

    for label in k3Labels:

        k3SliderAxes = plt.axes([0.65, bottom, width, height])
        if counter+1 <= min(len(ratek3), len(ratekCID)):
            k3SliderAxes.patch.set_facecolor(f"C{counter+1}")
            k3SliderAxes.patch.set_alpha(0.7)


        valmin = -33
        valmax = -25
        valstep = 1e-4
        
        
        if label in kvalueLimits:
            valmin, valmax, valinit = kvalueLimits[label]
        else:
            valinit=np.log10(ratek3[counter])

        print(valmin, valmax, valinit, flush=True)
        _k3Slider = Sliderlog( 
            ax=k3SliderAxes, label=label, 
            valmin=valmin, valmax=valmax, valinit=valinit, valstep=valstep, valfmt="%.2e",
        )

        _k3Slider.on_changed(update)
        # k3Sliders.append(_k3Slider)
        k3Sliders[label] = _k3Slider
        bottom -= height*1.2

        # if keyFoundForRate:
        counter += 1
    bottom -= height*2

    counter = 0
    for label in kCIDLabels:
        kCIDSliderAxes = plt.axes([0.65, bottom, width, height])
        if counter+1 <= min(len(ratek3), len(ratekCID)):
            kCIDSliderAxes.patch.set_facecolor(f"C{counter+1}")
            kCIDSliderAxes.patch.set_alpha(0.7)

        valmin = -20
        valmax = -10
        valstep = 1e-4
        
        if label in kvalueLimits:
            valmin, valmax, valinit = kvalueLimits[label]
        else:
            valinit=np.log10(ratekCID[counter])

        _kCIDSlider = Sliderlog(
            ax=kCIDSliderAxes, label=label, 
            valmin=valmin, valmax=valmax, valinit=valinit, valstep=valstep, valfmt="%.2e",
        )

        _kCIDSlider.on_changed(update)
        kCIDSliders[label] = _kCIDSlider


        bottom -= height*1.2
        # if keyFoundForRate:
        counter += 1
    return k3Sliders, kCIDSliders

if __name__ == "__main__":

    args = json.loads(sys.argv[1])
    # log(f"{args=}")

    currentLocation = pt(args["currentLocation"])
    data = args["data"]
    nameOfReactants = args["nameOfReactantsArray"]
    expTime = np.array(data[nameOfReactants[0]]["x"], dtype=float)*1e-3 # ms --> s
    expData = np.array([data[name]["y"] for name in nameOfReactants], dtype=float)
    expDataError = np.array([data[name]["error_y"]["array"] for name in nameOfReactants], dtype=float)

    log(f"{expTime.shape=}")
    log(f"{expData.shape=}")
    log(f"{expDataError.shape=}")
    
    temp = float(args["temp"])

    selectedFile = args["selectedFile"]
    numberDensity = float(args["numberDensity"])
    initialValues = [float(i) for i in args["initialValues"]]

    if "," in args["ratek3"]:
        k3Labels = [i.strip() for i in args["ratek3"].split(",")]
        kCIDLabels = [i.strip() for i in args["ratekCID"].split(",")]

    else:
        k3Labels = [args["ratek3"].strip()]
        kCIDLabels = [args["ratekCID"].strip()]


    totalAttachmentLevels = len(initialValues)-1
    savedir = currentLocation/"OUT"
    savefile = savedir/"k_fit.json"
    keyFoundForRate = False

    if savefile.exists():
        with open(savefile, "r") as f:

            k_fit_json = json.load(f)
            print(k_fit_json, flush=True)

            keyFound = selectedFile in k_fit_json
            print(f"{keyFound=}", flush=True)

            if keyFound:
                k_fit_values = k_fit_json[selectedFile]["k_fit"]

                ratek3 = np.asarray(k_fit_values[0], dtype=float)
                ratekCID = np.asarray(k_fit_values[1], dtype=float)
                keyFoundForRate = True

    if not keyFoundForRate:
        ratek3 = [float(args["k3Guess"]) for _ in k3Labels]
        ratekCID = [float(args["kCIDGuess"]) for _ in kCIDLabels]
    print(f"{keyFoundForRate=}\n{k3Labels=}", flush=True)

    
    # KineticMain = profile_line(KineticMain)
    KineticMain()
    # plt.show(block=False)
    plt.show()