from pathlib import Path as pt
import numpy as np
from felionlib.utils.felionQt import felionQtWindow


def main(args):

    files = [pt(i) for i in args["files"]]
    figArgs = args["figArgs"]

    widget = felionQtWindow(**figArgs)
    legend_handler = {}

    for file in files:
        x, y = [], []
        with open(file, "r") as f:
            for line in f.readlines():
                if line.startswith("#"):
                    continue
                data = line.split()

                if "x_type" in figArgs and figArgs["x_type"] == "float":
                    x.append(float(data[0]))
                else:
                    x.append(data[0])

                if "y_type" in figArgs and figArgs["y_type"] == "float":
                    y.append(float(data[1]))
                else:
                    y.append(data[1])

        if "labels" in figArgs and figArgs["labels"][file.name]:
            label = figArgs["labels"][file.name]
        else:
            label = file.stem

        (legend_handler[label],) = widget.ax.plot(x, y, label=label)

    widget.makeLegendToggler(legend_handler, edit_legend=True)
    widget.optimize_figure()
    widget.fig.tight_layout()
    widget.qapp.exec()
