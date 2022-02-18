
import json, traceback
from pathlib import Path as pt
import numpy as np
# import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from optimizePlot import optimizePlot
from matplotlib.widgets import Slider, Button, TextBox, CheckButtons
from scipy.optimize import curve_fit
from scipy.integrate import solve_ivp

from FELion_constants import pltColors
from FELion_definitions import readCodeFromFile
from FELion_widgets import FELion_Tk
from msgbox import MsgBox, MB_ICONERROR, MB_ICONINFORMATION


# from functools import reduce
def log(*msg): print(msg, flush=True)

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
            self.ax.figure.canvas.draw()
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
k_fit = []
def fitfunc(event=None):

    global k_fit, k_err

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

    except Exception:
        k_fit = []
        
        k_err = []
        if plotted:
            MsgBox("Error", traceback.format_exc(), MB_ICONERROR)


def saveData(event=None):
    try:
        
        savedir = currentLocation/"OUT"
        if not savedir.exists():
            savedir.mkdir()

        savefile = savedir/"k_fit.json"

        k3Len = len(ratek3)

        with open(savefile, "w+") as f:

            k3Values = (formatArray(rateCoefficientArgs[0]), formatArray(k_fit[:k3Len]) )[len(k_fit)>0]
            k3Err = ([0]*len(k3Labels), formatArray(k_err[:k3Len]))[len(k_err)>0]
            
            kCIDValues = (formatArray(rateCoefficientArgs[1]), formatArray(k_fit[k3Len:]))[len(k_fit)>0]
            kCIDErr = ([0]*len(kCIDLabels), formatArray(k_err[k3Len:]))[len(k_err)>0]

            k3_fit = {
                key: [value, err]
                for key, value, err in zip( k3Labels, k3Values,  k3Err )
            }
            kCID_fit = {
                key: [value, err]
                for key, value, err in zip( kCIDLabels, kCIDValues, kCIDErr )
            }
            
            dataToSave = {selectedFile : {}}
            dataToSave[selectedFile] = {
                "k3_fit": k3_fit,
                "kCID_fit": kCID_fit,
                "temp": f"{temp:.1f}",
                "numberDensity": f"{numberDensity:.2e}"
            }
            data = json.dumps({**rateConstantsFileData, **dataToSave}, sort_keys=True, indent=4, separators=(',', ': '))

            f.write(data)
            log(f"file written: {savefile.name} in {currentLocation} folder")
            if plotted: 
                MsgBox(
                    "Saved", 
                    f"Rate constants written in json format : '{savefile.name}'\nLocation: {currentLocation}", MB_ICONINFORMATION
                )

            fig.savefig(f"{savedir/selectedFile}_.png", dpi=200)
            fig.savefig(f"{savedir/selectedFile}_.pdf", dpi=200)


        with open(currentLocation/f"EXPORT/{selectedFile}_fitted.json", "w+") as f:
            dataToSaveFit = {"fit": {}, "exp": {}}
            for name, fitLine, expLine in zip(nameOfReactants, fitPlot, expPlot):
                xdata_f, ydata_f = fitLine.get_data()
                xdata, ydata = expLine.get_children()[0].get_data()
                dataToSaveFit["fit"][name] = {
                    "xdata": xdata_f.tolist(),
                    "ydata": ydata_f.tolist()
                }
                dataToSaveFit["exp"][name] = {
                    "xdata": xdata,
                    "ydata": ydata
                }
            
            data = json.dumps(dataToSaveFit, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(data)
            log(f"file written: {selectedFile}_fitted.json in EXPORT folder")

    except Exception:
        
        error = traceback.format_exc()
        if plotted: 
            MsgBox(
            "Error occured: ", 
            f"Error occured while saving the file\n{error}", 
            MB_ICONERROR
        )
        log(f"Error occured while saving the file\n{error}" )

fig = None
ax = None
canvas = None
fitPlot = []
expPlot = []
plotted=False

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
    canvas.draw()

def on_pick(event):
    
    legline = event.artist
    
    origlinefit, origlineexp = toggleLine[legline]

    alpha = 1 if origlinefit.get_alpha() < 1 else 0.2
    origlinefit.set_alpha(alpha)

    for _line in origlineexp.get_children():
        _line.set_alpha(alpha)
    
    legline.set_alpha(alpha)

    canvas.draw()

toggleLine = {}

def plot_exp():
    global data, fig, canvas, ax, k3Sliders, kCIDSliders, rateCoefficientArgs, \
        saveButton, radio, toggleLine, widget

    fig, canvas = widget.Figure()
    ax = widget.make_figure_layout(title=f"{selectedFile}", xaxis="Time (ms)", yaxis="Counts", yscale="log", savename=selectedFile)
    fig.subplots_adjust(right=0.6, top=0.95, left=0.09, bottom=0.25)

    # print(fig, canvas)
    
    axcolor = 'lightgoldenrodyellow'
    k3Sliders, kCIDSliders = make_slider()
    left, bottom, width, height = 0.1, 0.05, 0.1, 0.05
    
    buttonAxes = fig.add_axes([left, bottom, width, height], facecolor=axcolor)
    button = Button(buttonAxes, 'Fit', color=axcolor, hovercolor='0.975')

    button.on_clicked(fitfunc)

    left += width+0.01
    checkAxes = fig.add_axes([left, bottom, width, height], facecolor=axcolor)
    checkbox = CheckButtons(checkAxes, ("setbound", ), list(checkboxes.values()))
    checkbox.on_clicked(checkboxesFunc)

    left += width+0.01

    saveButtonAxes = fig.add_axes([left, bottom, width, height], facecolor=axcolor)
    saveButton = Button(saveButtonAxes, 'saveData', color=axcolor, hovercolor='0.975')
    saveButton.on_clicked(saveData)

    numberDensityWidgetAxes = fig.add_axes([0.9-width, bottom, width, height], facecolor=axcolor)
    numberDensityWidget = TextBox(numberDensityWidgetAxes, 'Number density', initial=f"{numberDensity:.2e}")
    numberDensityWidget.on_submit(setNumberDensity)

    for counter, key in enumerate(data.keys()):
        time = data[key]["x"]
        counts = data[key]["y"]
        error = data[key]["error_y"]["array"]
        _expPlot = ax.errorbar(time, counts, error, fmt=".", ms=10, label=key, c=pltColors[counter], alpha=1)

        expPlot.append(_expPlot)

    ax = optimizePlot(ax, xlabel="Time (ms)", ylabel="Counts", yscale="log")
    ax.set_ylim(ymin=0.1)
    ax.set_title(f"{selectedFile}: @{temp:.1f} K {numberDensity:.2e}"+"$cm^{-3}$")
    rateCoefficientArgs=(ratek3, ratekCID)
    
    log(f"{rateCoefficientArgs=}")
    log(f"{initialValues=}")

    dNdt = solve_ivp(compute_attachment_process, tspan, initialValues, dense_output=True)
    log(f"{dNdt=}")

    dNdtSol = dNdt.sol(simulateTime)
    for counter, data in enumerate(dNdtSol):
        _fitPlot, = ax.plot(simulateTime*1e3, data, "-", c=pltColors[counter], alpha=1)
        fitPlot.append(_fitPlot)

    widget.plot_legend = legend = ax.legend([f"${_}$" for _ in nameOfReactants])
    for legline, origlinefit, origlineexp in zip(legend.get_lines(), fitPlot, expPlot):
        legline.set_picker(True)
        toggleLine[legline] = [origlinefit, origlineexp]

    canvas.mpl_connect('pick_event', on_pick)

    try:
        global plotted
        if numberDensity > 0 and not keyFoundForRate:

            log("Fitting data")
            fitfunc()
        else:
            log("NOT fitting data since keyFoundForRate", keyFoundForRate)
        plotted = True

    except Exception:
        log(traceback.format_exc())
    canvas.draw()
    return numberDensityWidget, saveButton, checkbox, button

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

    canvas.draw()

k3Sliders = {}
kCIDSliders = {}

def make_slider():

    global k3Sliders, kCIDSliders
    ax.margins(x=0)
    
    height = 0.03
    width = 0.25
    bottom = 0.9

    counter = 0

    for label in k3Labels:
        k3SliderAxes = fig.add_axes([0.65, bottom, width, height])
        if counter+1 <= min(len(ratek3), len(ratekCID)):
            k3SliderAxes.patch.set_facecolor(f"C{counter+1}")
            k3SliderAxes.patch.set_alpha(0.7)


        valmin = -33
        valmax = -25
        valstep = 1e-4
        
        if label in kvalueLimits:
            valmin, valmax, valinit = kvalueLimits[label]
            if keyFoundForRate:
                valinit=np.log10(ratek3[counter])

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
        kCIDSliderAxes = fig.add_axes([0.65, bottom, width, height])
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

args = None
widget = None

def main(arguments):
    global args, currentLocation, nameOfReactants, \
        expTime, expData, expDataError, temp, rateConstantsFileData,\
        numberDensity, totalAttachmentLevels, selectedFile, initialValues, \
        k3Labels, kCIDLabels, ratek3, ratekCID, savedir, savefile, keyFoundForRate, data, widget
        

    args = arguments
    currentLocation = pt(args["currentLocation"]).parent
    data = args["data"]

    nameOfReactants = args["nameOfReactantsArray"]
    expTime = np.array(data[nameOfReactants[0]]["x"], dtype=float)*1e-3 # ms --> s
    expData = np.array([data[name]["y"] for name in nameOfReactants], dtype=float)
    expDataError = np.array([data[name]["error_y"]["array"] for name in nameOfReactants], dtype=float)
    
    temp = float(args["temp"])
    selectedFile = args["selectedFile"]
    
    numberDensity = float(args["numberDensity"])
    initialValues = [float(i) for i in args["initialValues"]]
    totalAttachmentLevels = len(initialValues)-1

    savedir = currentLocation/"OUT"
    savefile = savedir/"k_fit.json"

    keyFoundForRate = False
    rateConstantsFileData =  {}


    if savefile.exists():

        with open(savefile, "r") as f:
            keyFound = False

            rateConstantsFileContents = f.read()
            if len(rateConstantsFileContents)>0:
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
                print(len(args["ratek3"].split(",")) == len(k3Labels), "here", flush=True)
                print(len(args["ratekCID"].split(",")) == len(kCIDLabels), "here", flush=True)
                
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

    print(f"{keyFoundForRate=}\n{k3Labels=}", flush=True)
    print(f"{ratek3=}", flush=True)

    widget = FELion_Tk(title=f"Kinetics: {selectedFile}", location=savedir)
    KineticMain()
    # plt.show()

    # widget.plot_legend = ax.legend()
    widget.mainloop()