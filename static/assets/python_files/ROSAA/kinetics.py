
from re import T
import sys, json
from pathlib import Path as pt
import numpy as np
import matplotlib.pyplot as plt
from optimizePlot import optimizePlot

from matplotlib.widgets import Slider
# from scipy.optimize import curve_fit
from scipy.integrate import solve_ivp


# main_module_loc = str(pt(__file__).joinpath("../../"))
# sys.path.insert(0, main_module_loc)
# from FELion_definitions import sendData

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

def compute_attachment_process(t, N, k3, kCID):


    N0 = N[0]
    N_He = N[1:]
    attachmentRate = - k3[0]*numberDensity**2*N0 + kCID[0]*numberDensity*N_He[0]

    N0 = attachmentRate
    dR_dt = [N0]

    currentRate =  -attachmentRate

    for i in range(totalAttachmentLevels-1):
        nextRate = - k3[i+1]*numberDensity**2*N_He[i] + kCID[i+1]*numberDensity*N_He[i+1]
        attachmentRate = currentRate + nextRate
        dR_dt.append(attachmentRate)
        currentRate = -nextRate
    
    dR_dt.append(currentRate)
    return dR_dt


tspan = None
simulateTime = None
def KineticMain():


    global initialValues, tspan, simulateTime
    duration = time.max()*1.2
    tspan = [0, duration]
    simulateTime = np.linspace(0, duration, 1000)
    plot_exp()

    return


fig = None

ax = None
fitPlot = []

def plot_exp():
    global data, fig, ax, k3Sliders, kCIDSliders
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.subplots_adjust(right=0.6)

    k3Sliders, kCIDSliders = make_slider(ax)
    print(f"{k3Sliders=}", flush=True)
    for key in data.keys():
        expTime = data[key]["x"]
        counts = data[key]["y"]
        error = data[key]["error_y"]["array"]
        ax.errorbar(expTime, counts, error, fmt=".", ms=10, label=key)
    ax = optimizePlot(ax, xlabel="Time (s)", ylabel="Counts", yscale="log")

    dNdt = solve_ivp(compute_attachment_process, tspan, initialValues, args=(ratek3, ratekCID), dense_output=True)
    dNdtSol = dNdt.sol(simulateTime)

    for data in dNdtSol:

        _fitPlot, = ax.plot(simulateTime*1e3, data, "-")
        fitPlot.append(_fitPlot)
    plt.show()

def update(val):
    args=([10**rate.val for rate in k3Sliders], [10**rate.val for rate in kCIDSliders])

    dNdt = solve_ivp(compute_attachment_process, tspan, initialValues, args=args, dense_output=True)
    dNdtSol = dNdt.sol(simulateTime)

    for line, data in zip(fitPlot, dNdtSol):
        line.set_ydata(data)
    fig.canvas.draw_idle()

k3Sliders = []
kCIDSliders = []

def make_slider(ax):

    global k3Sliders, kCIDSliders
    axcolor = 'lightgoldenrodyellow'
    ax.margins(x=0)
    
    height = 0.03
    width = 0.25
    
    
    bottom = 0.7

    for label in k3Labels:
        k3SliderAxes = plt.axes([0.65, bottom, width, height], facecolor=axcolor)

        _k3Slider = Sliderlog( ax=k3SliderAxes, label=label, valmin=-33, valmax=-25, valinit=-30, valstep=0.01, valfmt="%.2e")
        _k3Slider.on_changed(update)
        k3Sliders.append(_k3Slider)
        
        bottom -= height*1.2

    bottom -= height*2
    for label in kCIDLabels:
        
        kCIDSliderAxes = plt.axes([0.65, bottom, width, height], facecolor=axcolor)
        _kCIDSlider = Sliderlog( ax=kCIDSliderAxes, label=label, valmin=-20, valmax=-10, valinit=-15, valstep=0.01, valfmt="%.2e")
        _kCIDSlider.on_changed(update)
        kCIDSliders.append(_kCIDSlider)
        bottom -= height*1.2

    return k3Sliders, kCIDSliders

if __name__ == "__main__":

    args = json.loads(sys.argv[1])
    currentLocation = pt(args["currentLocation"])

    data = args["data"]
    nameOfReactants = args["nameOfReactantsArray"]
    # print(data, flush=True)

    selectedFile = args["selectedFile"]

    numberDensity = float(args["numberDensity"])
    initialValues = [float(i) for i in args["initialValues"]]

    
    time = np.array(data[nameOfReactants[0]]["x"], dtype=float)*1e-3 # ms --> s
    if "," in args["ratek3"]:

        k3Labels = [i.strip() for i in args["ratek3"].split(",")]
        kCIDLabels = [i.strip() for i in args["ratekCID"].split(",")]

    else:
        k3Labels = [args["ratek3"].strip()]
        kCIDLabels = [args["ratekCID"].strip()]

    
    totalAttachmentLevels = len(initialValues)-1
    
    print(f"{k3Labels=}\n{totalAttachmentLevels=}", flush=True)
    ratek3 = [float(args["k3Guess"]) for _ in k3Labels]
    
    ratekCID = [float(args["kCIDGuess"]) for _ in kCIDLabels]
    print(f"{ratek3=}\n{nameOfReactants=}", flush=True)
    KineticMain()