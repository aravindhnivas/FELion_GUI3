import traceback
import numpy as np

from matplotlib.axes import Axes

from .rateSliders import make_slider
from .configfile import keyFoundForRate
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
    print(f"widgets removed", flush=True)


def on_pick(event):

    if widget.legendDraggableCheckWidget.isChecked():
        return

    legline = event.artist
    if not legline in toggleLine:
        return

    origlinefit, origlineexp = toggleLine[legline]
    alpha = 1 if origlinefit.get_alpha() < 1 else 0.2
    origlinefit.set_alpha(alpha)
    for _line in origlineexp.get_children():
        _line.set_alpha(alpha)

    legline.set_alpha(alpha)
    widget.draw()


def plot_exp():

    from felionlib.kineticsCode.utils.fit import intialize_fit_plot

    global toggleLine, widget, fitPlot, expPlot, data

    title = f"{selectedFile}: @{temp:.1f}K {numberDensity:.2e} " + "cm$^{-3}$"
    ax: Axes = widget.ax
    ax.set(xlabel="Time (s)", ylabel="Counts", yscale="log", title=title)

    widget.fig.subplots_adjust(**kinetic_plot_adjust_configs_obj)
    make_slider()

    for counter, key in enumerate(data.keys()):
        time = np.array(data[key]["x"], dtype=float) * 1e-3  # ms -> s
        counts = data[key]["y"]
        error = data[key]["error_y"]["array"]
        _expPlot = ax.errorbar(time, counts, error, fmt=".", ms=7, label=key, c=pltColors[counter], alpha=1)

        expPlot.append(_expPlot)

    ax.set_ylim(ymin=0.1)

    dNdtSol = intialize_fit_plot()

    for counter, data in enumerate(dNdtSol):

        (_fitPlot,) = ax.plot(simulateTime, data, "-", c=pltColors[counter], alpha=1, animated=True)
        fitPlot.append(_fitPlot)

    widget.blit = BlitManager(widget.canvas, fitPlot)

    legend = ax.legend(legends)
    for legline, origlinefit, origlineexp in zip(legend.get_texts(), fitPlot, expPlot):
        legline.set_picker(True)
        toggleLine[legline] = [origlinefit, origlineexp]

    widget.canvas.mpl_connect("pick_event", on_pick)
    widget.draw()
    