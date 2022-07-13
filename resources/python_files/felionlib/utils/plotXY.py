from pathlib import Path as pt
import numpy as np
from felionlib.utils.felionQt import felionQtWindow


def main(args):
    files = [pt(i) for i in args["files"]]
    location = files[0].parent
    figArgs = args["figArgs"]
    # title = args["title"]
    # xlabel = args["xlabel"]
    # ylabel = args["ylabel"]
    
    widget = felionQtWindow(**figArgs)
        # title=title,
        # figXlabel=xlabel,
        # figYlabel=ylabel,
        # ticks_direction="out",
        # location=location / "OUT",
        # savefilename="savefigure",
        # yscale="log",
    # )

    legend_handler = {}
    for file in files:
        masses_temp, counts_temp = np.genfromtxt(file).T
        (legend_handler[file.stem],) = widget.ax.plot(masses_temp, counts_temp, label=file.stem)

    widget.makeLegendToggler(legend_handler, edit_legend=True)
    widget.optimize_figure()
    widget.fig.tight_layout()
    widget.qapp.exec()
    