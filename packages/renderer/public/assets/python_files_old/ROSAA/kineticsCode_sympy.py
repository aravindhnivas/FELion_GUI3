
import sys
import json
from pprint import PrettyPrinter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox, CheckButtons
from optimizePlot import optimizePlot
from pathlib import Path as pt
# from FELion_definitions import readCodeFromFile
from symfit import variables, Parameter, ODEModel, D, Fit, parameters, Variable


main_module_loc = str(pt(__file__).joinpath("../../"))
sys.path.insert(0, main_module_loc)
from FELion_constants import pltColors
from FELion_definitions import readCodeFromFile, profile_line
def runCode(code):
    exec(code)
    return locals()

def logmsg(msg): print(msg, flush=True)
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


ode_model = None
simulateTime = None

def KineticMain():
    
    global ode_model, simulateTime


    duration = expTime.max()*1.2
    simulateTime = np.linspace(0, duration, 1000)

    location = pt(args["kineticEditorLocation"])
    filename = pt(location) / args["kineticEditorFilename"]
    codeContents = readCodeFromFile(filename)
    codeOutput = runCode(codeContents)
    # codeOutput = runCodeFromMarkedDownFile(filename)
    logmsg(f"{codeOutput=}")
    ode_model = codeOutput["ode_model"]

    pp.pprint(f"{ode_model=}\n{type(ode_model)=}")
    pp.pprint(f"{ode_model.model_dict=}")
    
    plot_exp_fn = profile_line(plot_exp)
    plot_exp_fn()
    # plot_exp()

    return

fig, ax = None, None
fitPlot = []
plotted=False

def ChangeYScale(yscale):
    ax.set_yscale(yscale)
    fig.canvas.draw_idle()

def setNumberDensity(val):
    global numberDensity
    numberDensity = float(val)
    logmsg(f"{numberDensity=}")

    ax.set_title(f"{selectedFile}: {temp:.1f} K {numberDensity:.2e}"+"$cm^{-3}$")
    # fitfunc()

# checkboxes = {
#     "setbound": False
# }


# def checkboxesFunc(label):
#     global checkboxes
#     checkboxes[label] = not checkboxes[label]
#     fig.canvas.draw_idle()

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

    # left += width+0.01
    # buttonAxes = plt.axes([left, bottom, width, height], facecolor=axcolor)
    # button = Button(buttonAxes, 'Fit', color=axcolor, hovercolor='0.975')
    # button.on_clicked(fitfunc)

    # left += width+0.01
    # checkAxes = plt.axes([left, bottom, width, height], facecolor=axcolor)
    # checkbox = CheckButtons(checkAxes, ("setbound", ), list(checkboxes.values()))
    
    # checkbox.on_clicked(checkboxesFunc)

    # left += width+0.01

    # saveButtonAxes = plt.axes([left, bottom, width, height], facecolor=axcolor)
    # saveButton = Button(saveButtonAxes, 'saveData', color=axcolor, hovercolor='0.975')
    # saveButton.on_clicked(saveData)

    numberDensityWidgetAxes = plt.axes([0.9-width, bottom, width, height], facecolor=axcolor)
    numberDensityWidget = TextBox(numberDensityWidgetAxes, 'Number density', initial=f"{numberDensity:.2e}")
    numberDensityWidget.on_submit(setNumberDensity)

    for counter, key in enumerate(data.keys()):
        time = data[key]["x"]

        counts = data[key]["y"]
        error = data[key]["error_y"]["array"]
        ax.errorbar(time, counts, error, fmt=".", ms=10, label=key, c=pltColors[counter])

    ax = optimizePlot(ax, xlabel="Time (ms)", ylabel="Counts", yscale="log")
    # logmsg(f"{temp=}")

    ax.set_title(f"{selectedFile}: @{temp:.1f} K {numberDensity:.2e}"+"$cm^{-3}$")
    
    rateCoefficientArgs = {
        key: value
        for key, value in zip(
            k3Labels+kCIDLabels,
            np.append(np.array(ratek3)*numberDensity**2, np.array(ratekCID)*numberDensity)
        )
    }

    logmsg(f"{rateCoefficientArgs=}\n")
    logmsg(f"{ode_model.initial=}")
    pp.pprint(f"{ode_model.model_dict=}")
    # return

    dNdtSol = ode_model(t=simulateTime, **rateCoefficientArgs)
    # dNdtSol = ode_model(t=simulateTime, k31=0.02, k32=0.02, kCID1=0.2, kCID2=0.2)
    for counter, data in enumerate(dNdtSol):
        _fitPlot, = ax.plot(simulateTime*1e3, data, "-", c=pltColors[counter])
        fitPlot.append(_fitPlot)

    legend = ax.legend([f"${_}$" for _ in nameOfReactants])
    legend.set_draggable(True)

    # try:
    #     global plotted
    #     if numberDensity > 0 and not keyFoundForRate:
    #         fitfunc()
    #     plotted = True

    # except Exception as error:
    #     logmsg(error)
    # plt.show()

rateCoefficientArgs = {}

def update(val=None):
    global rateCoefficientArgs

    rateCoefficientArgs = {
        key: value
        for key, value in zip(
            k3Labels+kCIDLabels,
            [10**rate.val*numberDensity**2 for rate in k3Sliders]+[10**rate.val*numberDensity for rate in kCIDSliders]
        )
    }
    dNdtSol = ode_model(t=simulateTime, **rateCoefficientArgs)

    for line, data in zip(fitPlot, dNdtSol):
        line.set_ydata(data)
    fig.canvas.draw_idle()
    
# update = profile_line(fitData)

k3Sliders = []
kCIDSliders = []

def make_slider(ax, axcolor):
    global k3Sliders, kCIDSliders

    ax.margins(x=0)
    

    height = 0.03
    width = 0.25
    bottom = 0.9

    counter = 0

    for label in k3Labels:
        k3SliderAxes = plt.axes([0.65, bottom, width, height], facecolor=axcolor)
        _k3Slider = Sliderlog( ax=k3SliderAxes, label=label, valmin=-33, valmax=-25, valinit=np.log10(ratek3[counter]), valstep=1e-4, valfmt="%.2e")
        _k3Slider.on_changed(update)
        k3Sliders.append(_k3Slider)
        bottom -= height*1.2
        # if keyFoundForRate:
        #     counter += 1

    bottom -= height*2

    counter = 0
    for label in kCIDLabels:

        kCIDSliderAxes = plt.axes([0.65, bottom, width, height], facecolor=axcolor)
        _kCIDSlider = Sliderlog( ax=kCIDSliderAxes, label=label, valmin=-20, valmax=-10, valinit=np.log10(ratekCID[counter]), valstep=1e-4, valfmt="%.2e")
        _kCIDSlider.on_changed(update)

        kCIDSliders.append(_kCIDSlider)
        bottom -= height*1.2
        # if keyFoundForRate:
        #     counter += 1
    return k3Sliders, kCIDSliders

# def plotFigure():
    
#     global fig, ax
#     fig, ax = plt.subplots()
#     counter = 0

#     for key, data in args["data"].items():
#         ax.errorbar(time, data["y"], yerr=data["error_y"]["array"], label=key, fmt=".-", c=f"C{counter}")
#         counter += 1
#     ax = optimizePlot(ax, "Time (ms)", "Counts", "log")
#     return

if __name__ == "__main__":
    args = json.loads(sys.argv[1])
    pp = PrettyPrinter(indent=4)

    # pp.pprint(args)

    # nameOfReactants = args["nameOfReactantsArray"]
    # time = args["data"][nameOfReactants[0]]["x"]

    # KineticMain()
    # plotFigure()
    # plt.tight_layout()
    # plt.show()


    data = args["data"]

    nameOfReactants = args["nameOfReactantsArray"]

    expTime = np.array(data[nameOfReactants[0]]["x"], dtype=float)*1e-3 # ms --> s
    expData = np.array([data[name]["y"] for name in nameOfReactants], dtype=float)
    expDataError = np.array([data[name]["error_y"]["array"] for name in nameOfReactants], dtype=float)

    logmsg(f"{expTime.shape=}")
    logmsg(f"{expData.shape=}")
    logmsg(f"{expDataError.shape=}")

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
    
    ratek3 = [float(args["k3Guess"]) for _ in k3Labels]
    ratekCID = [float(args["kCIDGuess"]) for _ in kCIDLabels]
    
    # KineticMain = profile_line(KineticMain)
    KineticMain()
    # plt.show(block=False)
    plt.show()