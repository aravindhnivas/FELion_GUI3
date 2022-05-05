import traceback
from matplotlib.axes import Axes
import numpy as np
from .rateSliders import make_slider
from felionlib.utils.FELion_constants import pltColors
from scipy.integrate import solve_ivp
from felionlib.utils.felionQt.utils.blit import BlitManager
import json

widget = None
otherWidgetsToggle = False


def hideOtherWidgets(event=None):
    global otherWidgetsToggle
    for otherWidget in widget.sliderWidgets:
        otherWidget.set_visible(otherWidgetsToggle)
    widget.draw()
    otherWidgetsToggle = not otherWidgetsToggle
    print(f"widgets removed", flush=True)


checkboxes = {"setbound": False}
toggleLine = {}


def on_pick(event):
    legline = event.artist
    origlinefit, origlineexp = toggleLine[legline]
    alpha = 1 if origlinefit.get_alpha() < 1 else 0.2
    origlinefit.set_alpha(alpha)
    for _line in origlineexp.get_children():
        _line.set_alpha(alpha)

    legline.set_alpha(alpha)
    widget.draw()


def plot_exp(
    compute_attachment_process,
    _widget,
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
    kinetic_plot_adjust_configs_obj
):

    global toggleLine, widget

    widget = _widget

    data = args["data"]
    temp = float(args["temp"])
    molecule = args["molecule"]

    # kinetic_plot_adjust_configs_obj = {
    #     key: float(value) for key, value in args["kinetic_plot_adjust_configs_obj"].items()
    # }
    # print(f"{kinetic_plot_adjust_configs_obj=}", flush=True)

    tag = args["tag"]
    selectedFile = args["selectedFile"]
    numberDensity = float(args["numberDensity"])
    nameOfReactants = args["nameOfReactantsArray"]
    initialValues = [float(i) for i in args["initialValues"]]

    expTime = np.array(data[nameOfReactants[0]]["x"], dtype=float) * 1e-3  # ms --> s
    duration = expTime.max() * 1.2

    tspan = [0, duration]
    simulateTime = np.linspace(0, duration, 1000)

    title = f"{selectedFile}: @{temp:.1f}K {numberDensity:.2e} " + "cm$^{-3}$"
    ax: Axes = widget.ax
    ax.set(xlabel="Time (s)", ylabel="Counts", yscale="log", title=title)
    widget.fig.subplots_adjust(**kinetic_plot_adjust_configs_obj)
    # if kinetic_plot_adjust_configs_obj:
    # else:
    #     widget.fig.subplots_adjust(right=0.570, top=0.900, left=0.120, bottom=0.160)

    k3Sliders, kCIDSliders = make_slider(
        widget,
        k3Labels,
        kCIDLabels,
        ratek3,
        ratekCID,
        kvalueLimits,
        keyFoundForRate,
        update,
    )

    for counter, key in enumerate(data.keys()):

        time = np.array(data[key]["x"], dtype=float) * 1e-3  # ms -> s

        counts = data[key]["y"]
        error = data[key]["error_y"]["array"]
        _expPlot = ax.errorbar(time, counts, error, fmt=".", ms=7, label=key, c=pltColors[counter], alpha=1)

        expPlot.append(_expPlot)

    ax.set_ylim(ymin=0.1)

    dNdtSol = solve_ivp(
        compute_attachment_process,
        tspan,
        initialValues,
        method="Radau",
        t_eval=simulateTime,
    ).y

    for counter, data in enumerate(dNdtSol):

        (_fitPlot,) = ax.plot(simulateTime, data, "-", c=pltColors[counter], alpha=1, animated=True)
        fitPlot.append(_fitPlot)

    widget.blit = BlitManager(widget.canvas, fitPlot)

    legends = [f"{molecule}$^+$", f"{molecule}$^+${tag}"]
    legends += [f"{molecule}$^+${tag}$_{i}$" for i in range(2, len(nameOfReactants))]

    legend = ax.legend(legends)

    for legline, origlinefit, origlineexp in zip(legend.get_lines(), fitPlot, expPlot):
        legline.set_picker(True)
        toggleLine[legline] = [origlinefit, origlineexp]

    widget.canvas.mpl_connect("pick_event", on_pick)

    try:
        if numberDensity > 0 and not keyFoundForRate:
            print("Fitting data", flush=True)
            fitfunc()
        else:
            print("NOT fitting data since keyFoundForRate", keyFoundForRate, flush=True)
    except Exception:
        print(traceback.format_exc(), flush=True)

    widget.draw()
    plotted = True

    return plotted, k3Sliders, kCIDSliders
