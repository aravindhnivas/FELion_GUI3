
import traceback
import numpy as np
from .rateSliders import make_slider
# from .plotWidgets import make_widgets
from felionlib.utils.FELion_constants import pltColors
from scipy.integrate import solve_ivp

widget = None
otherWidgetsToggle = False
# plotted = False


def hideOtherWidgets(event=None):
    global otherWidgetsToggle

    for otherWidget in widget.sliderWidgets:
        otherWidget.set_visible(otherWidgetsToggle)

    widget.canvas.draw_idle()
    otherWidgetsToggle = not otherWidgetsToggle
    print(f"widgets removed", flush=True)


checkboxes = {
    "setbound": False
}


toggleLine = {}


def on_pick(event):
    legline = event.artist
    origlinefit, origlineexp = toggleLine[legline]

    alpha = 1 if origlinefit.get_alpha() < 1 else 0.2
    origlinefit.set_alpha(alpha)
    for _line in origlineexp.get_children():
        _line.set_alpha(alpha)

    legline.set_alpha(alpha)
    widget.canvas.draw_idle()


def plot_exp(
    compute_attachment_process, _widget, k3Labels, kCIDLabels, ratek3,
    ratekCID, kvalueLimits, keyFoundForRate, update, expPlot, fitPlot, args,
    fitfunc
):

    global toggleLine, widget

    widget = _widget

    data = args["data"]
    temp = float(args["temp"])
    molecule = args["molecule"]

    tag = args["tag"]
    selectedFile = args["selectedFile"]
    numberDensity = float(args["numberDensity"])
    nameOfReactants = args["nameOfReactantsArray"]
    initialValues = [float(i) for i in args["initialValues"]]

    expTime = np.array(data[nameOfReactants[0]]["x"],
                       dtype=float)*1e-3  # ms --> s
    duration = expTime.max()*1.2

    tspan = [0, duration]
    simulateTime = np.linspace(0, duration, 1000)

    widget.Figure()

    title = f"{selectedFile}: @{temp:.1f} K {numberDensity:.2e}"+"$cm^{-3}$"
    
    ax = widget.make_figure_layout(
        xaxis="Time (ms)", yaxis="Counts",

        yscale="log", optimize=True,
        title=title, savename=selectedFile,
    )

    widget.fig.subplots_adjust(right=0.6, top=0.95, left=0.09, bottom=0.25)

    # saveDataArgs = (
    #     args, ratek3, k3Labels, kCIDLabels, k_fit, k_err, rateCoefficientArgs,
    #     fitPlot, expPlot, rateConstantsFileData
    # )
    # make_widgets(
    #     widget=widget, fitfunc=fitfunc, 
    #     numberDensity=numberDensity, saveDataArgs=saveDataArgs
    # )

    k3Sliders, kCIDSliders = make_slider(
        widget, k3Labels, kCIDLabels,
        ratek3, ratekCID, kvalueLimits,
        keyFoundForRate, update
    )

    for counter, key in enumerate(data.keys()):

        time = data[key]["x"]
        counts = data[key]["y"]
        error = data[key]["error_y"]["array"]
        _expPlot = ax.errorbar(
            time, counts, error,
            fmt=".", ms=10, label=key,
            c=pltColors[counter], alpha=1
        )

        expPlot.append(_expPlot)

    ax.set_ylim(ymin=0.1)

    dNdtSol = solve_ivp(
        compute_attachment_process, tspan, initialValues,
        method="Radau", t_eval=simulateTime
    ).y

    for counter, data in enumerate(dNdtSol):

        _fitPlot, = ax.plot(
            simulateTime*1e3, data, "-",
            c=pltColors[counter], alpha=1
        )

        fitPlot.append(_fitPlot)

    legends = [f"{molecule}$^+$", f"{molecule}$^+${tag}"]
    legends += [
        f"{molecule}$^+${tag}$_{i}$"
        for i in range(2, len(nameOfReactants))
    ]

    widget.plot_legend = legend = ax.legend(legends)

    for legline, origlinefit, origlineexp in zip(
        legend.get_lines(), fitPlot, expPlot
    ):
        legline.set_picker(True)
        toggleLine[legline] = [origlinefit, origlineexp]

    widget.canvas.mpl_connect('pick_event', on_pick)

    try:
        if numberDensity > 0 and not keyFoundForRate:
            print("Fitting data", flush=True)

            fitfunc()
        else:
            print(
                "NOT fitting data since keyFoundForRate", keyFoundForRate,
                flush=True
            )

    except Exception:
        print(traceback.format_exc(), flush=True)

    widget.canvas.draw_idle()
    widget.last_y = widget.last_y + widget.y_diff
    widget.Buttons(
        "Toggle-Widgets", widget.x0, widget.last_y,
        hideOtherWidgets, relwidth=0.7
    )

    plotted = True
    print(f"{plotted=}", flush=True)

    return plotted, k3Sliders, kCIDSliders