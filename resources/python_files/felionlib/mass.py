from pathlib import Path as pt
import numpy as np
from felionlib.utils.felionQt import felionQtWindow
from PyQt6.QtWidgets import QApplication
from felionlib.utils.FELion_definitions import var_find


def main(args):

    qapp = QApplication([])
    massfiles = [pt(i) for i in args["massfiles"]]
    location = massfiles[0].parent

    widget = felionQtWindow(title=f"Mass spectrum",
        figXlabel="m/z", figYlabel="Counts", ticks_direction="out",
        location=location/"OUT", savefilename="masspec", yscale="log"
    )

    legend_handler = {}

    for massfile in massfiles:
        masses_temp, counts_temp = np.genfromtxt(massfile).T
        res, b0, trap = var_find(massfile)
        label = f"{massfile.stem}: Res:{res}; B0: {b0}ms; trap: {trap}ms"
        (legend_handler[label],) = widget.ax.plot(masses_temp, counts_temp, label=label)

    widget.makeLegendToggler(legend_handler)
    widget.optimize_figure()
    widget.fig.tight_layout()
    qapp.exec()
    