import numpy as np
from matplotlib.axes import Axes
from .rateSliders import make_slider
from felionlib.kineticsCode import (
    kinetic_plot_adjust_configs_obj,
    legends,
    simulateTime,
    selectedFile,
    temp,
    numberDensity,
    widget,
    data,
)

from felionlib.utils.FELion_constants import pltColors
from felionlib.utils.felionQt.utils.blit import BlitManager


otherWidgetsToggle = False
fitPlot: list[Axes] = []
expPlot: list[Axes] = []
toggleLine = {}


def hideOtherWidgets(event=None):
    global otherWidgetsToggle
    for otherWidget in widget.sliderWidgets:
        otherWidget.set_visible(otherWidgetsToggle)
    widget.draw()
    otherWidgetsToggle = not otherWidgetsToggle


def on_pick(event):
    if widget.legendDraggableCheckWidget.isChecked():
        return

    legline = event.artist
    if not legline in toggleLine:
        return

    origlinefit, origlineexp = toggleLine[legline]
    alpha = 1 if origlinefit.get_alpha() < 1 else 0.2
    origlinefit.set_alpha(alpha)

    for child in origlineexp.get_children():
        child.set_alpha(alpha)
    legline.set_alpha(alpha)
    widget.draw()


def get_time_and_counts_and_error(obj):
    time = np.array(obj["x"], dtype=float) * 1e-3  # ms -> s
    counts = obj["y"]
    error = obj["error_y"]["array"]
    return time, counts, error


def plot_exp():

    from felionlib.kineticsCode.utils.fit import intialize_fit_plot

    global toggleLine, widget, fitPlot, expPlot

    title = f"{selectedFile}: @{temp:.1f}K {numberDensity:.2e} " + "cm$^{-3}$"
    ax: Axes = widget.ax
    ax.set(xlabel="Time (s)", ylabel="Counts", yscale="log", title=title)

    widget.fig.subplots_adjust(**kinetic_plot_adjust_configs_obj)
    make_slider()

    for counter, key in enumerate(data.keys()):

        if not key == "SUM":
            time, counts, error = get_time_and_counts_and_error(data[key])
            _expPlot = ax.errorbar(time, counts, error, fmt=".", ms=7, label=key, c=pltColors[counter], alpha=1)
            expPlot.append(_expPlot)

    exp_sum_data = get_time_and_counts_and_error(data["SUM"])
    exp_sum_plot = ax.errorbar(
        exp_sum_data[0], exp_sum_data[1], yerr=exp_sum_data[2], fmt=".", label="SUM", ms=7, c="k", alpha=1
    )
    expPlot.append(exp_sum_plot)

    ax.set_ylim(ymin=0.1)
    dNdtSol = intialize_fit_plot()

    for counter, fitted_data in enumerate(dNdtSol):
        (_fitPlot,) = ax.plot(simulateTime, fitted_data, "-", c=pltColors[counter], alpha=1, animated=True)
        fitPlot.append(_fitPlot)

    fitted_sum = dNdtSol.sum(axis=0)
    (fitted_sum_plot,) = ax.plot(simulateTime, fitted_sum, "-", c="k", alpha=1, animated=True)
    fitPlot.append(fitted_sum_plot)

    widget.blit = BlitManager(widget.canvas, fitPlot)
    legend = ax.legend([*legends, "SUM"])
    for legline, origlinefit, origlineexp in zip(legend.get_texts(), fitPlot, expPlot):
        legline.set_picker(True)
        toggleLine[legline] = [origlinefit, origlineexp]
    # widget.canvas.mpl_connect("pick_event", on_pick)
    widget.make_legend_editor(on_pick_callback=on_pick)
    widget.draw()
