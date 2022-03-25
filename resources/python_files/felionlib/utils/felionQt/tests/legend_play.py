from matplotlib.artist import Artist
from typing import Union, Iterable
from matplotlib.container import Container
import numpy as np
from .. import felionQtWindow

def main():

    widget = felionQtWindow(title="legend_play", includeCloseEvent=False)
    x = np.arange(0.1, 4, 0.1)
    y1 = np.exp(-1.0 * x)
    y2 = np.exp(-0.5 * x)
    y1err = 0.1 + 0.1 * np.sqrt(x)
    y2err = 0.1 + 0.1 * np.sqrt(x / 2)

    line_handler: dict[str, Union[Union[Container, Artist], Iterable[Union[Container, Artist]]]] = {}
    errorbarHandler1 = widget.ax.errorbar(x, y1, yerr=y1err, label="plot_legend_errorbar")
    errorbarHandler2 = widget.ax.errorbar(x, y2, yerr=y2err)
    line_handler["plot_legend_errorbar"] = [errorbarHandler1, errorbarHandler2]
    (line_handler["plot_legend_line"],) = widget.ax.plot(x, y2 - 0.5, label="plot_legend_line")
    (line_handler["plot_legend_line_dashed"],) = widget.ax.plot(x, y2 + 0.5, "--", label="plot_legend_line_dashed")
    (line_handler["plot_legend_line_dot"],) = widget.ax.plot(x, y2 + 1, ".-", label="plot_legend_line_dot")
    (line_handler["plot_legend_dot"],) = widget.ax.plot(x, y2 - 1, ".", label="plot_legend_dot")

    widget.updatecanvas()
    widget.makeLegendToggler(line_handler)